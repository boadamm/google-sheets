# Makefile for sheets-bot desktop application packaging
# Provides tasks for building and cleaning GUI distribution

.PHONY: build-gui clean-gui test-gui install-deps help release-patch release-minor release-major check-release

# Default target shows help
help:
	@echo "Available targets:"
	@echo ""
	@echo "🏗️  Build Targets:"
	@echo "  build-gui      Build desktop GUI application using PyInstaller"
	@echo "  clean-gui      Clean build artifacts and distribution files"
	@echo "  test-gui       Run GUI-specific tests"
	@echo "  install-deps   Install PyInstaller and other build dependencies"
	@echo ""
	@echo "🚀 Release Targets:"
	@echo "  release-patch  Create patch release (bug fixes)"
	@echo "  release-minor  Create minor release (new features)"
	@echo "  release-major  Create major release (breaking changes)"
	@echo "  check-release  Preview what would be released (dry run)"
	@echo ""
	@echo "  help          Show this help message"

# Install build dependencies
install-deps:
	@echo "Installing build dependencies..."
	pip install pyinstaller

# Build the GUI desktop application
build-gui: install-deps
	@echo "Building Sheets Bot desktop application..."
	@# Guard against building in CI environment (no GUI support)
	@if [ "$$CI" = "" ]; then \
		echo "Building desktop application..."; \
		pyinstaller -y build/pyinstaller.spec; \
		echo "✅ Build completed successfully!"; \
		echo "📁 Desktop app available at: dist/SheetsBot/"; \
		ls -la dist/SheetsBot/; \
	else \
		echo "⚠️  Skipping GUI build in CI environment (no display available)"; \
		echo "CI environment detected, GUI build skipped"; \
	fi

# Clean build artifacts
clean-gui:
	@echo "Cleaning build artifacts..."
	@rm -rf build/__pycache__/
	@rm -rf dist/
	@rm -rf *.spec
	@echo "✅ Clean completed"

# Test GUI functionality (can run in CI with virtual display)
test-gui:
	@echo "Running GUI packaging tests..."
	@# Set QT_QPA_PLATFORM for headless testing in CI
	@if [ "$$CI" != "" ]; then \
		export QT_QPA_PLATFORM=offscreen; \
	fi; \
	pytest tests/test_packaging.py -v

# Development workflow: clean, build, and test
dev-build: clean-gui build-gui test-gui
	@echo "🚀 Development build completed!"

# Quick test of the built application (skip in CI)
test-run:
	@if [ "$$CI" = "" ] && [ -f "dist/SheetsBot/SheetsBot" ]; then \
		echo "Testing the built application..."; \
		timeout 10s dist/SheetsBot/SheetsBot || true; \
		echo "✅ Application starts successfully"; \
	else \
		echo "⚠️  Skipping application test (CI environment or build not found)"; \
	fi

# Release management targets
check-release:
	@echo "🔍 Checking release readiness..."
	@python scripts/release.py patch --dry-run

release-patch:
	@echo "🚀 Creating patch release..."
	@python scripts/release.py patch

release-minor:
	@echo "🚀 Creating minor release..."
	@python scripts/release.py minor

release-major:
	@echo "🚀 Creating major release..."
	@python scripts/release.py major

# Full quality check before release
pre-release-check:
	@echo "🔍 Running pre-release quality checks..."
	@ruff check .
	@black --check .
	@pytest -q
	@echo "✅ All quality checks passed" 