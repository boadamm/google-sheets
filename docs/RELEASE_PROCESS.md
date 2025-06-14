# SheetsBot Release Process & News Distribution

This guide explains how to create releases and distribute news for the SheetsBot project.

## 🚀 Release Process

### Quick Release (Recommended)

Use our automated release script for streamlined releases:

```bash
# Patch release (bug fixes)
python scripts/release.py patch

# Minor release (new features)
python scripts/release.py minor --changes "Added new file monitoring features"

# Major release (breaking changes)
python scripts/release.py major --changes "Complete GUI redesign"

# Dry run to preview changes
python scripts/release.py patch --dry-run
```

### Manual Release Process

If you prefer manual control:

1. **Update Version Numbers**
   ```bash
   # Update version in setup.py and app/gui/main_window.py
   # Current version: 1.0.0
   ```

2. **Update Changelog**
   ```bash
   # Add new section to CHANGELOG.md
   ## [1.0.1] - 2024-01-15
   
   ### Added
   - New feature descriptions
   
   ### Fixed  
   - Bug fix descriptions
   ```

3. **Run Quality Checks**
   ```bash
   ruff check .
   black --check .
   pytest --cov=. --cov-report=term-missing
   ```

4. **Create Git Tag**
   ```bash
   git add .
   git commit -m "chore: bump version to 1.0.1"
   git tag -a v1.0.1 -m "Release v1.0.1"
   git push
   git push --tags
   ```

5. **GitHub Actions Automation**
   - Release workflow automatically triggers on tag push
   - Creates release artifacts (Linux, Windows, source)
   - Publishes GitHub Release with changelog
   - Updates README download links

## 📢 News & Announcements

### Automatic News Distribution

Our system automatically handles news distribution:

**On Release:**
- ✅ Creates GitHub Release with formatted notes
- ✅ Generates GitHub Discussion in Announcements category
- ✅ Updates README badges and download links
- ✅ Extracts changelog entries for release notes

### Manual Announcements

#### Method 1: GitHub Issues (Recommended)
1. Create new issue using "📢 Announcement" template
2. Fill out the structured form
3. Add `announcement` label
4. System auto-creates GitHub Discussion
5. Issue gets marked as `published`

#### Method 2: GitHub Actions Workflow
1. Go to Actions → "News & Announcements"
2. Click "Run workflow"
3. Select announcement type
4. Enter title and message
5. Creates GitHub Discussion automatically

#### Method 3: GitHub Discussions (Direct)
1. Go to repository Discussions
2. Create new discussion in "Announcements" category
3. Use emoji prefixes: 🚀 📢 🎉 🔒

### News Categories

| Type | Emoji | Use Case |
|------|-------|----------|
| Release | 🚀 | New version announcements |
| Feature | 🎉 | New feature highlights |
| Security | 🔒 | Security updates/patches |
| General | 📢 | Community updates |
| Documentation | 📚 | Docs updates |
| Event | 📅 | Roadmap/events |

## 🎯 Release Checklist

### Pre-Release
- [ ] All tests passing (`pytest -q`)
- [ ] Code quality checks pass (`ruff check .` + `black --check .`)
- [ ] CHANGELOG.md updated with changes
- [ ] Version numbers updated in all files
- [ ] Documentation updated if needed
- [ ] Breaking changes documented

### Release
- [ ] Git tag created and pushed
- [ ] GitHub Actions workflow completed successfully
- [ ] Release artifacts generated (Linux, Windows, source)
- [ ] GitHub Release created with proper notes
- [ ] Download links working

### Post-Release
- [ ] GitHub Discussion created for community
- [ ] README badges updated automatically
- [ ] Community notified
- [ ] Social media announcements (if applicable)
- [ ] Monitor for feedback and issues

## 🔧 Configuration

### GitHub Repository Settings
1. **Enable Discussions**: Settings → Features → Discussions ✅
2. **Create Discussion Categories**:
   - 📢 Announcements (for news)
   - 💬 General (for community chat)
   - ❓ Q&A (for support)
   - 💡 Ideas (for feature requests)

### Required Secrets
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

### Branch Protection
- Protect `main` branch
- Require status checks
- Require up-to-date branches

## 📊 Metrics & Tracking

The system automatically tracks:
- Release frequency
- Community engagement (discussions, comments)
- Download statistics
- Issue/bug reports

## 🛠️ Troubleshooting

### Release Script Issues
```bash
# Check current version
python -c "from scripts.release import get_current_version; print(get_current_version())"

# Validate changelog format
grep -n "## \[" CHANGELOG.md

# Test without making changes
python scripts/release.py patch --dry-run
```

### GitHub Actions Failures
1. Check Actions tab for error logs
2. Verify repository permissions
3. Ensure GITHUB_TOKEN has necessary scopes
4. Check file paths in workflows

### Missing Discussions
1. Enable Discussions in repository settings
2. Create "Announcements" category
3. Re-run the news workflow

## 📚 Examples

### Example Release Command
```bash
# Create a patch release with custom changelog
python scripts/release.py patch --changes "
### Added
- New CSV processing engine
- Improved error handling

### Fixed  
- Memory leak in file watcher
- GUI responsiveness issues
"
```

### Example Manual Announcement
```markdown
## 🎉 SheetsBot v1.2.0 - New GUI Release!

We're excited to announce SheetsBot v1.2.0 with a completely redesigned user interface!

### ✨ What's New
- Modern PySide6-based GUI
- Dark mode support
- Improved file processing workflows
- Better error reporting

### 📥 Download
- **Quick Install**: `curl -sSL https://github.com/boadamm/demoproject/raw/main/install.sh | bash`
- **Manual**: [Download from releases](https://github.com/boadamm/demoproject/releases/latest)

### 🐛 Known Issues
- Windows installer signing in progress
- Minor UI glitches on high-DPI displays

**Thank you to all contributors!** 🙏
```

## 🔗 Related Documentation

- [Contributing Guidelines](../CONTRIBUTING.md)
- [Installation Guide](../INSTALLATION.md)
- [API Setup Guide](../API_SETUP_GUIDE.md)
- [Changelog](../CHANGELOG.md) 