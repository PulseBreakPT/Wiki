#!/usr/bin/env bash
# Run ONCE on your own trusted computer. This script never uploads or prints the private key.
set -euo pipefail
umask 077
if [ "$#" -ne 1 ]; then
  printf 'Usage: bash scripts/create-android-keystore.sh /absolute/private/backup-directory\n' >&2
  exit 1
fi
command -v keytool >/dev/null || { printf 'Install JDK 17 first.\n' >&2; exit 1; }
repo="$(cd "$(dirname "$0")/.." && pwd -P)"
mkdir -p "$1"
out="$(cd "$1" && pwd -P)"
case "$out/" in "$repo/"*) printf 'Choose a private directory OUTSIDE the repository.\n' >&2; exit 1;; esac
key="$out/viarchive-release.jks"
if [ -e "$key" ] || [ -e "$key.b64" ]; then
  printf 'A key/backup already exists. Reuse it; do not overwrite a permanent signing identity.\n' >&2
  exit 1
fi
keytool -genkeypair -keystore "$key" -storetype PKCS12 -alias viarchive \
  -keyalg RSA -keysize 4096 -validity 10000 \
  -dname 'CN=VI Archive, OU=Android, O=VI Archive, C=PT'
base64 < "$key" | tr -d '\r\n' > "$key.b64"
printf '\nKey created once in your private backup directory.\n'
printf 'Configure GitHub Secrets: ANDROID_KEYSTORE_B64 (contents of .jks.b64), ANDROID_KEY_ALIAS (viarchive), ANDROID_STORE_PASSWORD and ANDROID_KEY_PASSWORD (the password you just chose, same value for PKCS12).\n'
printf 'Keep an encrypted backup. Never commit these files or share the key in chat.\n'
