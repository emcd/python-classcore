# Release Patch Command

Execute a fully automated postrelease patch following LLM-guided release best practices.

This command implements the proven process documented in the AAR for automated patch releases with GitHub Actions monitoring.

## Usage

```
/release-patch
```

## Prerequisites

Before running this command, ensure:
- All patch fixes are committed to `master` branch
- You have identified the specific commit hashes to cherry-pick
- GitHub CLI (`gh`) is installed and authenticated
- Release branch exists (e.g., `release-1.6`)

## Process

The command will guide you through:

1. **Checkout Release Branch**: Switch to the appropriate release branch
2. **Cherry-pick Commits**: Apply fixes from master to release branch  
3. **Version Bump**: Increment patch version using `hatch version patch`
4. **Update Changelog**: Run Towncrier to build changelog
5. **QA Monitoring**: Push commits and monitor QA workflow with GitHub CLI
6. **Tag Release**: Create signed git tag after QA passes
7. **Release Monitoring**: Monitor release workflow deployment
8. **Cleanup**: Remove news fragments and cherry-pick back to master

## GitHub CLI Monitoring

The process uses optimized GitHub CLI commands for real-time workflow monitoring:

- `gh run watch --compact --interval 30` for efficient token usage
- Two-phase validation: QA workflow → Release workflow
- Automatic halt on any failures for human consultation

## Safety Features

- **Validation at each step**: Process halts if any step fails
- **Real-time status reporting**: Clear progress updates throughout
- **Error handling**: Immediate stop for manual intervention if needed
- **Git hygiene**: Maintains clean commit history and proper branching

## Command Sequence

Execute these commands in order, adapting commit hashes and version numbers as needed:

```bash
# 1. Checkout and Prepare Release Branch
git checkout release-X.Y  # Replace X.Y with actual version
git pull origin release-X.Y

# 2. Cherry-pick Patch Commits from Master  
git cherry-pick <commit-hash-1>  # Replace with actual commit hash
git cherry-pick <commit-hash-2>  # Add more as needed
git cherry-pick <commit-hash-3>

# 3. Bump to Patch Version
hatch version patch
git add . && git commit -m "Bump version to $(hatch version)."

# 4. Run Towncrier to Build Changelog
hatch --env develop run towncrier build --keep --version $(hatch version)
git add . && git commit -m "Update changelog for v$(hatch version) patch release."

# 5. Push Commits and Monitor QA
git push origin release-X.Y
gh run list --workflow=qa --limit=1
gh run watch <qa-run-id> --interval 30 --compact

# 6. Tag the Patch Release (After QA Passes)
git tag -m "Release v$(hatch version) patch: <brief-description>." v$(hatch version)
git push --tags

# 7. Monitor Release Workflow  
gh run list --workflow=release --limit=1
gh run watch <release-run-id> --interval 30 --compact

# 8. Clean Up News Fragments (After Release Completes)
git rm .auxiliary/data/towncrier/*.rst
git commit -m "Clean up news fragments."
git push origin release-X.Y

# 9. Cherry-pick Back to Master
git checkout master
git pull origin master
git cherry-pick <changelog-commit-hash>
git cherry-pick <cleanup-commit-hash>  
git push origin master
```

**Example from v1.6.1 release:**
```bash
# Used actual commit hashes: 3063e6c, 3e2e5a5, b72125d
# Monitored workflows: 16015567174 (QA), 16015632051 (Release)
# Description: "Fix deprecation warnings from finalize_module"
```

This automation is based on the first successful fully LLM-guided release process, validated with real deployment to PyPI and GitHub.