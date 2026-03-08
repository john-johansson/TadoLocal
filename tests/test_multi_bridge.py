"""Tests for multi-bridge/accessory ip:pin argument parsing."""
import argparse
from tado_local.__main__ import _parse_ip_pin_args


def _make_parser():
    """Build a minimal parser matching __main__.py's bridge/accessory args."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--bridge', action='append', default=[])
    parser.add_argument('--bridge-ip', dest='bridge_ip')
    parser.add_argument('--pin')
    parser.add_argument('--accessory', action='append', default=[])
    parser.add_argument('--accessory-ip', action='append', default=[], dest='accessory_ip')
    parser.add_argument('--accessory-pin', action='append', default=[], dest='accessory_pin')
    return parser


class TestParseIpPinArgs:
    def test_single_with_pin(self):
        assert _parse_ip_pin_args(['192.168.1.1:111-11-111']) == [('192.168.1.1', '111-11-111')]

    def test_single_without_pin(self):
        assert _parse_ip_pin_args(['192.168.1.1']) == [('192.168.1.1', None)]

    def test_two_with_pins(self):
        result = _parse_ip_pin_args(['192.168.1.1:111-11-111', '192.168.1.2:222-22-222'])
        assert result == [('192.168.1.1', '111-11-111'), ('192.168.1.2', '222-22-222')]

    def test_mixed_pin_and_no_pin(self):
        result = _parse_ip_pin_args(['192.168.1.1:111-11-111', '192.168.1.2'])
        assert result == [('192.168.1.1', '111-11-111'), ('192.168.1.2', None)]

    def test_three_entries(self):
        result = _parse_ip_pin_args(['192.168.1.1:111-11-111', '192.168.1.2:222-22-222', '192.168.1.3'])
        assert len(result) == 3
        assert result[2] == ('192.168.1.3', None)

    def test_empty_list(self):
        assert _parse_ip_pin_args([]) == []


class TestBridgeArgFallback:
    def test_legacy_bridge_ip_pin_not_in_bridge_list(self):
        """Legacy --bridge-ip / --pin falls back correctly when no --bridge given."""
        parser = _make_parser()
        args = parser.parse_args(['--bridge-ip', '192.168.1.1', '--pin', '111-11-111'])
        bridges = _parse_ip_pin_args(args.bridge)
        assert bridges == []
        assert args.bridge_ip == '192.168.1.1'
        assert args.pin == '111-11-111'

    def test_auto_discovery_when_nothing_specified(self):
        """No --bridge and no --bridge-ip means auto-discovery from DB."""
        parser = _make_parser()
        args = parser.parse_args([])
        bridges = _parse_ip_pin_args(args.bridge)
        assert bridges == []
        assert args.bridge_ip is None


class TestAccessoryArgParsing:
    def test_single_with_pin(self):
        assert _parse_ip_pin_args(['192.168.1.101:987-65-432']) == [('192.168.1.101', '987-65-432')]

    def test_single_without_pin(self):
        assert _parse_ip_pin_args(['192.168.1.101']) == [('192.168.1.101', None)]

    def test_two_accessories(self):
        result = _parse_ip_pin_args(['192.168.1.101:987-65-432', '192.168.1.102'])
        assert result == [('192.168.1.101', '987-65-432'), ('192.168.1.102', None)]
