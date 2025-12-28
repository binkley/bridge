#!/usr/bin/env bash

set -euo pipefail

# Default values
readonly BATCH_SIZE=40
readonly DEFAULT_COUNT=1000

usage() {
    cat <<EOF
Usage: $(basename "$0") [options] [command]

Options:
  -h, --help       Show this help message and exit

Commands:
  generate [args]  Run the deal generator (e.g., -n 100)
  evaluate [args]  Run the DDS evaluator (accepts PBN via STDIN)
  test             Run the 100% coverage audit trail
  pipeline [N]     Run E2E simulation (default N=$DEFAULT_COUNT)
EOF
}

cmd_generate() { python3 generate-hands.py "$@"; }

cmd_evaluate() {
    # Maintaining DDS stability for M3 Max
    python3 evaluate-hands.py --batch-size "$BATCH_SIZE" "$@"
}

cmd_test() { ./docker-test.sh; }

cmd_pipeline() {
    local count=${1:-$DEFAULT_COUNT}
    echo "🚀 Running $count hand simulation..."
    python3 generate-hands.py -n "$count" | cmd_evaluate
}

main() {
    # Parse top-level options
    while (( $# > 0 )); do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            -*)
                echo "Unknown option: $1" >&2
                usage
                exit 1
                ;;
            *)
                break # First non-flag argument is our subcommand
                ;;
        esac
    done

    # Default to pipeline if no subcommand is provided
    if (( $# == 0 )); then
        cmd_pipeline "$DEFAULT_COUNT"
        exit 0
    fi

    local subcmd=$1
    shift

    case "$subcmd" in
        generate) cmd_generate "$@" ;;
        evaluate) cmd_evaluate "$@" ;;
        test)     cmd_test ;;
        pipeline) cmd_pipeline "${1:-$DEFAULT_COUNT}" ;;
        *)
            echo "Unknown command: $subcmd" >&2
            usage
            exit 1
            ;;
    esac
}

main "$@"