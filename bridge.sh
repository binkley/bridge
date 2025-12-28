#!/usr/bin/env bash

set -euo pipefail

# Default values
readonly BATCH_SIZE=40

usage() {
    cat <<EOF
Usage: $(basename "$0") [options] [command]

Options:
  -h, --help       Show this help message and exit

Commands:
  generate N       Run the deal generator for N deals
  evaluate [args]  Run the DDS evaluator (accepts PBN via STDIN)
  test             Run the 100% coverage audit trail
  pipeline N       Run E2E simulation for N deals
EOF
}

cmd_generate() {
    # If N is missing, generate-hands.py will now throw a helpful error 
    python3 generate-hands.py "$@"
}

cmd_evaluate() {
    # Enforcing batch size for M3 Max C++ stability 
    python3 evaluate-hands.py --batch-size "$BATCH_SIZE" "$@"
}

cmd_test() {
    # Triggers the 90%+ coverage ratchet 
    ./docker-test.sh
}

cmd_pipeline() {
    if (( $# == 0 )); then
        echo "Error: pipeline requires a deal count (N)" >&2
        usage
        exit 1
    fi
    local count=$1
    echo "🚀 Running $count hand simulation..."
    python3 generate-hands.py "$count" | cmd_evaluate
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
                break 
                ;;
        esac
    done

    # Error if no subcommand is provided (removes accidental defaults)
    if (( $# == 0 )); then
        echo "Error: Command required" >&2
        usage
        exit 1
    fi

    local subcmd=$1
    shift

    case "$subcmd" in
        generate) cmd_generate "$@" ;;
        evaluate) cmd_evaluate "$@" ;;
        test)     cmd_test ;;
        pipeline) cmd_pipeline "$@" ;;
        *)
            echo "Unknown command: $subcmd" >&2
            usage
            exit 1
            ;;
    esac
}

main "$@"
