#!/usr/bin/env python3
"""
Test script for Blockly configuration system
"""

from config.blockly_config import (
    BlocklyConfig, BLOCK_REGISTRY, PRESETS,
    save_config, load_config, get_all_block_types
)

def test_presets():
    """Test all preset configurations"""
    print("=" * 60)
    print("TESTING PRESETS")
    print("=" * 60)

    for preset_name, config in PRESETS.items():
        print(f"\n{preset_name.upper()} Preset:")
        print(f"  - {len(config.enabled_blocks)} blocks enabled")
        print(f"  - {len(config.enabled_categories)} categories enabled")
        print(f"  - Categories: {', '.join(sorted(config.enabled_categories))}")

        # Check for missing dependencies
        missing = config.get_missing_dependencies()
        if missing:
            print(f"  ⚠️  WARNING: Missing dependencies detected!")
            for block_type, deps in missing.items():
                print(f"      {block_type} requires: {', '.join(deps)}")
        else:
            print(f"  ✓ All dependencies satisfied")

def test_persistence():
    """Test saving and loading configuration"""
    print("\n" + "=" * 60)
    print("TESTING PERSISTENCE")
    print("=" * 60)

    # Create a custom config
    print("\nCreating custom configuration...")
    custom_config = BlocklyConfig(preset_name="custom")
    custom_config.enable_block("event_create")
    custom_config.enable_block("event_step")
    custom_config.enable_block("move_set_hspeed")
    custom_config.enabled_categories.add("Events")
    custom_config.enabled_categories.add("Movement")

    print(f"Custom config: {len(custom_config.enabled_blocks)} blocks, {len(custom_config.enabled_categories)} categories")

    # Save it
    print("Saving configuration...")
    save_config(custom_config)

    # Load it back
    print("Loading configuration...")
    loaded_config = load_config()

    # Verify
    if loaded_config.enabled_blocks == custom_config.enabled_blocks:
        print("✓ Configuration saved and loaded correctly!")
    else:
        print("✗ Configuration mismatch!")
        print(f"  Expected: {custom_config.enabled_blocks}")
        print(f"  Got: {loaded_config.enabled_blocks}")

def test_dependencies():
    """Test dependency checking"""
    print("\n" + "=" * 60)
    print("TESTING DEPENDENCY CHECKING")
    print("=" * 60)

    # Create config with dependency issue
    print("\nCreating config with missing dependency...")
    config = BlocklyConfig(preset_name="test")
    config.enable_block("event_alarm")  # Requires set_alarm
    # Intentionally NOT enabling set_alarm

    missing = config.get_missing_dependencies()
    if missing:
        print("✓ Dependency checking works!")
        for block_type, deps in missing.items():
            print(f"  {block_type} requires: {', '.join(deps)}")
    else:
        print("✗ Dependency checking failed - should have detected missing set_alarm")

    # Now enable the dependency
    print("\nEnabling missing dependency...")
    config.enable_block("set_alarm")

    missing = config.get_missing_dependencies()
    if not missing:
        print("✓ Dependencies now satisfied!")
    else:
        print("✗ Still have missing dependencies")

def test_block_registry():
    """Test block registry integrity"""
    print("\n" + "=" * 60)
    print("TESTING BLOCK REGISTRY")
    print("=" * 60)

    total_blocks = 0
    for category, blocks in BLOCK_REGISTRY.items():
        print(f"\n{category}: {len(blocks)} blocks")
        total_blocks += len(blocks)

    print(f"\nTotal blocks in registry: {total_blocks}")

    # Verify all block types are unique
    all_types = get_all_block_types()
    print(f"Unique block types: {len(all_types)}")

    if len(all_types) == total_blocks:
        print("✓ All block types are unique")
    else:
        print("✗ Duplicate block types detected!")

def test_category_operations():
    """Test enabling/disabling categories"""
    print("\n" + "=" * 60)
    print("TESTING CATEGORY OPERATIONS")
    print("=" * 60)

    config = BlocklyConfig(preset_name="test")

    # Enable a category
    print("\nEnabling 'Events' category...")
    config.enable_category("Events")
    events_blocks = BLOCK_REGISTRY["Events"]

    enabled_count = sum(1 for b in events_blocks if config.is_block_enabled(b["type"]))
    print(f"Enabled {enabled_count} out of {len(events_blocks)} blocks")

    if enabled_count == len(events_blocks):
        print("✓ All blocks in category enabled")
    else:
        print("✗ Not all blocks enabled")

    # Disable the category
    print("\nDisabling 'Events' category...")
    config.disable_category("Events")

    enabled_count = sum(1 for b in events_blocks if config.is_block_enabled(b["type"]))
    if enabled_count == 0:
        print("✓ All blocks in category disabled")
    else:
        print(f"✗ Still have {enabled_count} blocks enabled")

def main():
    print("\n" + "=" * 60)
    print("BLOCKLY CONFIGURATION SYSTEM TEST SUITE")
    print("=" * 60)

    test_block_registry()
    test_presets()
    test_category_operations()
    test_dependencies()
    test_persistence()

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
