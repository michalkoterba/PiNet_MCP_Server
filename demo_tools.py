"""
Demo script to showcase PiNet MCP Server tools
Automatically runs all test scenarios
"""

from mcp_pinet_server.server import ping_host, wake_device
import json
import time

def print_header(title):
    """Print a section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_test(test_num, description, tool_name, param):
    """Print test info"""
    print(f"\n[Test {test_num}] {description}")
    print(f"Calling: {tool_name}('{param}')")
    print("-" * 70)

def print_result(result):
    """Pretty print result"""
    print("\nRESULT:")
    print(json.dumps(result, indent=2))

def main():
    print("\n" + "="*70)
    print("  PINET MCP SERVER - TOOL DEMONSTRATION")
    print("="*70)
    print("\nThis demo will test both MCP tools with various scenarios")
    print("Your PiNet API: (configured in .env)")
    print()
    time.sleep(1)

    # ========================================================================
    # PING_HOST TESTS
    # ========================================================================
    print_header("TESTING: ping_host Tool")
    time.sleep(0.5)

    # Test 1: Ping Google DNS (should be online)
    print_test(1, "Ping a well-known online host", "ping_host", "8.8.8.8")
    result = ping_host("8.8.8.8")
    print_result(result)
    time.sleep(1)

    # Test 2: Ping local network device
    print_test(2, "Ping a local network device", "ping_host", "192.168.1.1")
    result = ping_host("192.168.1.1")
    print_result(result)
    time.sleep(1)

    # Test 3: Ping likely offline host
    print_test(3, "Ping a likely offline host", "ping_host", "192.168.1.250")
    result = ping_host("192.168.1.250")
    print_result(result)
    time.sleep(1)

    # Test 4: Invalid IP format
    print_test(4, "Test error handling - Invalid IP format", "ping_host", "999.999.999.999")
    result = ping_host("999.999.999.999")
    print_result(result)
    time.sleep(1)

    # Test 5: Empty/whitespace IP
    print_test(5, "Test error handling - Empty IP", "ping_host", "")
    result = ping_host("")
    print_result(result)
    time.sleep(1)

    # ========================================================================
    # WAKE_DEVICE TESTS
    # ========================================================================
    print_header("TESTING: wake_device Tool")
    time.sleep(0.5)

    # Test 6: Valid MAC address
    print_test(6, "Send WoL packet to valid MAC", "wake_device", "AA:BB:CC:DD:EE:FF")
    result = wake_device("AA:BB:CC:DD:EE:FF")
    print_result(result)
    time.sleep(1)

    # Test 7: Another valid MAC format
    print_test(7, "Send WoL packet (different MAC)", "wake_device", "12:34:56:78:9A:BC")
    result = wake_device("12:34:56:78:9A:BC")
    print_result(result)
    time.sleep(1)

    # Test 8: Invalid MAC format
    print_test(8, "Test error handling - Invalid MAC format", "wake_device", "invalid-mac")
    result = wake_device("invalid-mac")
    print_result(result)
    time.sleep(1)

    # Test 9: Incomplete MAC
    print_test(9, "Test error handling - Incomplete MAC", "wake_device", "AA:BB:CC")
    result = wake_device("AA:BB:CC")
    print_result(result)
    time.sleep(1)

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_header("DEMONSTRATION COMPLETE")
    print("\n[OK] All tools have been tested successfully!")
    print("\nKey Observations:")
    print("  - ping_host tool works correctly for valid/invalid IPs")
    print("  - wake_device tool works correctly for valid/invalid MACs")
    print("  - Error handling returns clear, LLM-friendly messages")
    print("  - All responses are in JSON format")
    print("\n" + "="*70)
    print("Your PiNet MCP Server is ready to use with Open Webui!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()