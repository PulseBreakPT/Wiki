"""Load and project the editor-supplied SSS pre-release corpus.

The compressed payload is version-controlled. This module never invents missing fields:
Official, Development, Unknown and Reported remain distinct editorial states.
"""
from __future__ import annotations

import gzip
import json
import lzma
from collections import Counter
from copy import deepcopy
from pathlib import Path

SSS_CORPUS_PATH = Path(__file__).with_name("sss_corpus.json.xz")
SSS_MANAGED_AUTHOR = "Importação editorial SSS"
SSS_REVIEWER = "Revisão humana pendente"
SSS_REASON = "Importação do pacote editorial SSS de 11 de setembro de 2026."
LIVE_ROOT = "https://pulsebreakpt.github.io/Wiki/"

STATE_APPLICABILITY = {
    "Official": "Identificado como Official no dossiê fornecido, com suporte em material promocional ou comercial publicado; detalhes pré-lançamento ainda podem mudar.",
    "Development": "Identificado em material de desenvolvimento/pré-lançamento. Não deve ser tratado como conteúdo final até reconfirmação.",
    "Unknown": "O dossiê fornecido marca este ponto como desconhecido ou ainda não confirmado; não são inferidos valores em falta.",
    "Reported": "Identificação ou síntese editorial pré-lançamento. Deve permanecer separada de uma confirmação final da Rockstar.",
}

def load_sss_corpus():
    raw = SSS_CORPUS_PATH.read_bytes()
    payload = gzip.decompress(raw) if raw.startswith(b"\\x1f\\x8b") else lzma.decompress(raw)
    data = json.loads(payload.decode("utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("entities"), list):
        raise ValueError("Unsupported SSS corpus schema.")
    ids = [entity["id"] for entity in data["entities"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate entity identifiers in SSS corpus.")
    for event in data.get("timeline", []):
        if "/source-docs/" in event.get("source_url", ""):
            event["source_url"] = LIVE_ROOT
    return data

def applicability(state):
    return STATE_APPLICABILITY.get(state, STATE_APPLICABILITY["Reported"])

def expand_sss_claims(entity, recorded_at):
    claims = []
    for index, raw in enumerate(entity.get("claims", []), start=1):
        prop, value = raw[0], raw[1]
        extra = raw[2] if len(raw) > 2 else {}
        state = extra.get("state", entity.get("label", "Reported"))
        claims.append({
            "id": f"sss-{entity['id']}-{index:02d}",
            "entity_id": entity["id"],
            "property": prop,
            "value": value,
            "source_id": extra.get("source_id", entity["source_id"]),
            "excerpt": value,
            "locator": extra.get("locator", entity["name"]),
            "origin": "comunidade",
            "nature": extra.get("nature", "declaracao"),
            "verification": "pendente",
            "applicability": applicability(state),
            "method": "Importado do dossiê editorial pré-lançamento fornecido, sem inferir campos em falta.",
            "related_entity_id": extra.get("related_entity_id"),
            "spoiler": bool(extra.get("spoiler", False)),
            "reviewed_by": SSS_REVIEWER,
            "recorded_at": recorded_at,
        })
    return claims

async def seed_sss_corpus(db, now, project, current_publication):
    corpus = load_sss_corpus()
    recorded_at = now()
    source_accessed_at = corpus.get("snapshot_at") or recorded_at
    for source in corpus.get("sources", []):
        record = {**source, "accessed_at": source_accessed_at, "published_at": source.get("published_at")}
        await db.sources.update_one({"id": source["id"]}, {"$setOnInsert": record}, upsert=True)

    managed_authors = {"Importação de fontes oficiais", "Importação editorial documentada", SSS_MANAGED_AUTHOR}
    revision = int(corpus.get("revision", 1))
    for entity in corpus["entities"]:
        entity_id = entity["id"]
        await db.entities.update_one(
            {"id": entity_id},
            {"$setOnInsert": {"id": entity_id, "slug": entity.get("slug", entity_id), "type": entity["type"], "schema_version": 1}},
            upsert=True,
        )
        claims = expand_sss_claims(entity, recorded_at)
        for assertion in claims:
            await db.assertions.update_one({"id": assertion["id"]}, {"$setOnInsert": assertion}, upsert=True)

        current = await current_publication(entity_id)
        pub_id = f"sss-r{revision}-{entity_id}"
        if current and current.get("id") == pub_id:
            continue
        if current and current.get("author_name") not in managed_authors:
            continue
        if await db.publications.find_one({"id": pub_id}, {"_id": 0, "id": 1}):
            continue

        previous_snapshot = current.get("snapshot", {}) if current else {}
        snapshot = {
            "slug": entity.get("slug", entity_id),
            "name": entity["name"],
            "type": entity["type"],
            "aliases": entity.get("aliases", []),
            "summary": entity["summary"],
            "image": entity.get("image") or previous_snapshot.get("image", ""),
            "image_position": entity.get("image_position") or previous_snapshot.get("image_position", "center"),
            "label": entity.get("label", "Reported"),
        }
        old_ids = current.get("assertion_ids", []) if current else []
        assertion_ids = list(dict.fromkeys([*old_ids, *[claim["id"] for claim in claims]]))
        version = (current.get("version", 0) if current else 0) + 1
        publication = {
            "id": pub_id, "entity_id": entity_id, "version": version, "snapshot": snapshot,
            "assertion_ids": assertion_ids, "created_at": recorded_at,
            "author_name": SSS_MANAGED_AUTHOR, "reviewer_name": SSS_REVIEWER, "reason": SSS_REASON,
            "outbox": {"id": f"event-{pub_id}", "status": "pending", "attempts": 0},
        }
        await db.publications.update_one({"id": pub_id}, {"$setOnInsert": publication}, upsert=True)
        stored = await db.publications.find_one({"id": pub_id}, {"_id": 0})
        if stored:
            await project(stored)

    for event in corpus.get("timeline", []):
        await db.timeline.update_one({"id": event["id"]}, {"$setOnInsert": event}, upsert=True)

def merge_offline_corpus(base):
    corpus = load_sss_corpus()
    merged = deepcopy(base)
    timestamp = corpus.get("snapshot_at") or merged["snapshot_at"]

    source_map = {source["id"]: source for source in merged["sources"]}
    for raw in corpus.get("sources", []):
        source = {**raw, "accessed_at": timestamp, "published_at": raw.get("published_at")}
        source_map[source["id"]] = source
    merged["sources"] = list(source_map.values())

    by_id = {entity["id"]: entity for entity in merged["entities"]}
    history = merged["history"]
    revision = int(corpus.get("revision", 1))
    for raw in corpus["entities"]:
        entity_id = raw["id"]
        claims = expand_sss_claims(raw, timestamp)
        for claim in claims:
            claim["source"] = source_map.get(claim["source_id"])
        existing = by_id.get(entity_id)
        if existing:
            old_version = existing.get("version", 1)
            old_assertions = existing.get("assertions", [])
            assertions = list({claim["id"]: claim for claim in [*old_assertions, *claims]}.values())
            existing.update({
                "slug": raw.get("slug", entity_id), "name": raw["name"], "type": raw["type"],
                "aliases": raw.get("aliases", []), "summary": raw["summary"],
                "image": raw.get("image") or existing.get("image", ""),
                "image_position": raw.get("image_position") or existing.get("image_position", "center"),
                "label": raw.get("label", "Reported"), "version": old_version + 1,
                "updated_at": timestamp, "assertion_count": len(assertions), "assertions": assertions,
            })
            history[entity_id] = [{
                "id": f"sss-r{revision}-{entity_id}", "entity_id": entity_id, "version": existing["version"],
                "created_at": timestamp, "author_name": SSS_MANAGED_AUTHOR, "reviewer_name": SSS_REVIEWER,
                "reason": SSS_REASON, "snapshot": {k: v for k, v in existing.items() if k != "assertions"},
                "assertion_ids": [claim["id"] for claim in assertions],
            }, *history.get(entity_id, [])]
        else:
            entity = {
                "id": entity_id, "slug": raw.get("slug", entity_id), "name": raw["name"], "type": raw["type"],
                "aliases": raw.get("aliases", []), "summary": raw["summary"], "image": raw.get("image", ""),
                "image_position": raw.get("image_position", "center"), "label": raw.get("label", "Reported"),
                "version": 1, "updated_at": timestamp, "assertion_count": len(claims), "assertions": claims,
            }
            merged["entities"].append(entity)
            by_id[entity_id] = entity
            history[entity_id] = [{
                "id": f"sss-r{revision}-{entity_id}", "entity_id": entity_id, "version": 1,
                "created_at": timestamp, "author_name": SSS_MANAGED_AUTHOR, "reviewer_name": SSS_REVIEWER,
                "reason": SSS_REASON, "snapshot": {k: v for k, v in entity.items() if k != "assertions"},
                "assertion_ids": [claim["id"] for claim in claims],
            }]

    timeline = {event["id"]: event for event in merged.get("timeline", [])}
    timeline.update({event["id"]: event for event in corpus.get("timeline", [])})
    merged["timeline"] = sorted(timeline.values(), key=lambda event: event["date"], reverse=True)
    merged["snapshot_at"] = max(str(merged.get("snapshot_at", "")), str(timestamp))
    merged["origin"] = "backend/seed.py + editor-supplied SSS dossiers"
    merged["notice"] = (
        "Corpus versionado do VI Archive. Inclui o pacote editorial SSS fornecido para o arquivo; "
        "Official, Development, Unknown e Reported permanecem estados distintos e campos em falta não são inferidos."
    )
    merged["stats"] = {
        "entities": len(merged["entities"]), "sources": len(merged["sources"]),
        "assertions": sum(entity.get("assertion_count", 0) for entity in merged["entities"]),
        "types": dict(Counter(entity["type"] for entity in merged["entities"])),
    }
    return merged
