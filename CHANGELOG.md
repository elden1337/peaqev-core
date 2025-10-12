# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GE-Spot (Global Electricity Spot Prices) integration support
  - New `GESpotUpdater` class for handling GE-Spot price sensors
  - New `GESpotDTO` for transforming 15-minute interval data to hourly prices
  - Automatic detection of GE-Spot entities in `SpotPriceFactory`
  - Support for multi-region electricity pricing with fallback mechanisms
  - Comprehensive test coverage for GE-Spot functionality

### Changed
- `SpotPriceFactory` now prioritizes GE-Spot over other price sources when available
- Enhanced price source detection logic to support multiple integration types

## [19.11.4] - 2024-10-08

Previous stable release.

