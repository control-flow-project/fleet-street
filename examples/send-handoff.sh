#!/bin/sh
set -eu
if [ "$#" -ne 4 ]; then
  printf 'Usage: sh examples/send-handoff.sh ROOM_ID RECIPIENT_MATRIX_ID TRANSACTION_ID MARKDOWN_FILE\n' >&2
  exit 2
fi
: "${CROSSFIRE_PROJECT:?Use the project supplied by fleetd}"
: "${CROSSFIRE_AGENT_NAME:?Use the profile supplied by fleetd}"
node "$CROSSFIRE_PROJECT/.crossfire/client.mjs" \
  --project "$CROSSFIRE_PROJECT" --profile "$CROSSFIRE_AGENT_NAME" \
  matrix send-message --room-id "$1" --event-type m.room.message \
  --mention-user "$2" --txn-id "$3" --markdown-file "$4"
