<h3>Project 3 - Incremental File Syncer</h3>

Purpose: Sync files from source directory to target directory with incremental updates (only copy changed files).</br>
Not a full rsync, but a simplified, reliable tool.

</br>
<h5>Features:</h5>
<li>Scan source and target, compute file metadata (size, mtime, and optional hash).</li>
<li>Decide action per file: skip, copy/update, delete (if --delete specified).</li>
<li>CLI flags: --dry-run, --hash (use md5/sha1 to detect changes), --workers (parallel copy), --exclude patterns.</li>
<li>Logging for actions and summary report.</li>
<li>Safety: default no deletes, require --confirm for destructive ops.</li>
<li>Tests: unit tests for the decision logic (simulate file metadata), integration test with temp directories.</li>
<li>Packaging: syncer CLI.</li>

</br>
<h5>Stretch Features (for later):</h5>
<li>Use concurrent.futures to parallelize copying.</li>
<li>Implement resume support for partially copied files (temp filenames + atomic rename).</li>
<li>Use checksums only for files above size threshold to save time.</li>

<h5>Current status: Implementing core functionality</h5>
Acceptance:</br>
<li>python -m syncer --dry-run lists planned actions without modifying target.</li>
<li>With --confirm, it performs copy actions; with --delete --confirm it also deletes extras.</li>
<li>Tests for key behaviors.</li>
</br>
