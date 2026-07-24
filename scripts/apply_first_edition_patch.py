from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"marker not found in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


workflow = Path(".github/workflows/web-night-shift.yml")
replace_once(
    workflow,
    """      - .github/prompts/nightly-revise.prompt.yml
      - scripts/web_night_shift.py
""",
    """      - .github/prompts/nightly-revise.prompt.yml
      - press/series/the-one/bootstrap-selection.json
      - scripts/web_night_shift.py
""",
)

replace_once(
    workflow,
    """      - name: Record an idle night
        if: steps.resume.outputs.stop != 'true' && steps.prepare.outputs.due != 'true'
        run: |
          echo "No article was commissioned: ${{ steps.prepare.outputs.reason }}" >> "$GITHUB_STEP_SUMMARY"

      - name: Select the night's subject
        id: select
        if: steps.prepare.outputs.due == 'true'
        uses: actions/ai-inference@v2
        with:
          prompt-file: .github/prompts/nightly-select.prompt.yml
          file_input: |
            candidates: .nb-web/candidates.json
            recent: .nb-web/recent.json

      - name: Fetch and prove the source pack
        id: research
        if: steps.prepare.outputs.due == 'true'
        run: >-
          uv run scripts/web_night_shift.py research
          --selection "${{ steps.select.outputs.response-file }}"
""",
    """      - name: Determine whether the first edition needs a bootstrap commission
        id: bootstrap
        if: steps.resume.outputs.stop != 'true'
        run: |
          set -euo pipefail
          if find library-checkout/library/the-one -maxdepth 1 -type f -name '*.html' \
            -print -quit 2>/dev/null | grep -q .; then
            echo "use=false" >> "$GITHUB_OUTPUT"
          else
            echo "use=true" >> "$GITHUB_OUTPUT"
          fi

      - name: Record an idle night
        if: steps.resume.outputs.stop != 'true' && steps.prepare.outputs.due != 'true' && steps.bootstrap.outputs.use != 'true'
        run: |
          echo "No article was commissioned: ${{ steps.prepare.outputs.reason }}" >> "$GITHUB_STEP_SUMMARY"

      - name: Select the night's subject
        id: select
        if: steps.prepare.outputs.due == 'true' && steps.bootstrap.outputs.use != 'true'
        uses: actions/ai-inference@v2
        with:
          prompt-file: .github/prompts/nightly-select.prompt.yml
          file_input: |
            candidates: .nb-web/candidates.json
            recent: .nb-web/recent.json

      - name: Load the first-edition bootstrap commission
        id: bootstrap-select
        if: steps.bootstrap.outputs.use == 'true'
        run: |
          set -euo pipefail
          file="$GITHUB_WORKSPACE/press/series/the-one/bootstrap-selection.json"
          test -s "$file"
          echo "response-file=$file" >> "$GITHUB_OUTPUT"

      - name: Resolve the selection file
        id: selection
        if: steps.prepare.outputs.due == 'true' || steps.bootstrap.outputs.use == 'true'
        run: |
          set -euo pipefail
          if [ "${{ steps.bootstrap.outputs.use }}" = "true" ]; then
            file="${{ steps.bootstrap-select.outputs.response-file }}"
          else
            file="${{ steps.select.outputs.response-file }}"
          fi
          test -s "$file"
          echo "file=$file" >> "$GITHUB_OUTPUT"

      - name: Fetch and prove the source pack
        id: research
        if: steps.selection.outputs.file != ''
        run: >-
          uv run scripts/web_night_shift.py research
          --selection "${{ steps.selection.outputs.file }}"
""",
)

replace_once(
    workflow,
    "if: steps.prepare.outputs.due == 'true' && steps.research.outputs.ready != 'true'",
    "if: steps.selection.outputs.file != '' && steps.research.outputs.ready != 'true'",
)

Path(__file__).unlink()
