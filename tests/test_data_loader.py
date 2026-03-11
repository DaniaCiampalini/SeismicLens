"""
Test suite — utils/data_loader.py
Copre: generate_synthetic_quake, load_csv_signal, crustal_velocity_at_depth,
       travel_time_layered, fetch_fdsn_waveform (mock), FDSN_PROVIDERS dict.
"""

import io
import email.message
import unittest
from typing import cast
from unittest.mock import patch, MagicMock

import numpy as np

from utils.data_loader import (
    generate_synthetic_quake,
    load_csv_signal,
    crustal_velocity_at_depth,
    travel_time_layered,
    FDSN_PROVIDERS,
    CRUSTAL_LAYERS,
    fetch_fdsn_waveform,
)


# ─────────────────────────────────────────────────────────────────────────────
# generate_synthetic_quake
# ─────────────────────────────────────────────────────────────────────────────

class TestGenerateSyntheticQuake(unittest.TestCase):

    def setUp(self):
        self.signal, self.fs, self.meta = generate_synthetic_quake(
            magnitude=5.5, depth_km=30, dist_km=80,
            noise_level=0.1, duration_s=60.0, fs=100.0,
        )

    def test_returns_tuple_of_three(self):
        result = generate_synthetic_quake()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

    def test_signal_is_float64_array(self):
        self.assertIsInstance(self.signal, np.ndarray)
        self.assertEqual(self.signal.dtype, np.float64)

    def test_signal_length_matches_duration(self):
        expected_n = int(60.0 * 100.0)
        self.assertEqual(len(self.signal), expected_n)

    def test_sampling_rate_correct(self):
        self.assertAlmostEqual(self.fs, 100.0)

    def test_metadata_keys_present(self):
        required = {"type", "magnitude", "depth_km", "dist_km",
                    "p_arrival_s", "s_arrival_s", "sp_delay_s", "n_samples"}
        self.assertTrue(required.issubset(self.meta.keys()))

    def test_p_arrives_before_s(self):
        self.assertLess(self.meta["p_arrival_s"], self.meta["s_arrival_s"])

    def test_sp_delay_positive(self):
        self.assertGreater(self.meta["sp_delay_s"], 0)

    def test_signal_not_all_zeros(self):
        self.assertGreater(np.max(np.abs(self.signal)), 0)

    def test_amplitude_scales_with_magnitude(self):
        _, _, _ = generate_synthetic_quake(magnitude=3.0, duration_s=30)
        sig_large, _, _ = generate_synthetic_quake(magnitude=7.0, duration_s=30)
        sig_small, _, _ = generate_synthetic_quake(magnitude=3.0, duration_s=30)
        self.assertGreater(
            np.max(np.abs(sig_large)),
            np.max(np.abs(sig_small)),
        )

    def test_default_dist_km_computed_when_none(self):
        _, _, meta = generate_synthetic_quake(magnitude=5.0, depth_km=20, dist_km=None)
        self.assertGreater(meta["dist_km"], 0)

    def test_zero_noise_reproducible(self):
        s1, _, _ = generate_synthetic_quake(magnitude=5.0, noise_level=0.0, duration_s=10)
        s2, _, _ = generate_synthetic_quake(magnitude=5.0, noise_level=0.0, duration_s=10)
        np.testing.assert_array_equal(s1, s2)

    def test_metadata_type_is_synthetic(self):
        self.assertEqual(self.meta["type"], "synthetic")

    def test_vp_vs_ratio_stored(self):
        self.assertIn("vp_vs_ratio", self.meta)
        self.assertGreater(self.meta["vp_vs_ratio"], 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# load_csv_signal
# ─────────────────────────────────────────────────────────────────────────────

class TestLoadCsvSignal(unittest.TestCase):

    def _make_file(self, content: str) -> io.StringIO:
        return io.StringIO(content)

    def test_single_column_default_fs(self):
        csv = "amplitude\n1.0\n2.0\n3.0\n4.0\n"
        sig, fs, meta = load_csv_signal(self._make_file(csv))
        self.assertEqual(len(sig), 4)
        self.assertAlmostEqual(fs, 100.0)

    def test_two_column_fs_inferred(self):
        rows = "\n".join(f"{i*0.01},{np.sin(i*0.1):.6f}" for i in range(100))
        csv = "time_s,amplitude\n" + rows
        sig, fs, meta = load_csv_signal(self._make_file(csv))
        self.assertAlmostEqual(fs, 100.0, delta=1.0)
        self.assertEqual(len(sig), 100)

    def test_two_column_unnamed(self):
        rows = "\n".join(f"{i*0.01},{float(i):.1f}" for i in range(50))
        csv = "t,val\n" + rows
        sig, fs, meta = load_csv_signal(self._make_file(csv))
        self.assertEqual(len(sig), 50)

    def test_metadata_has_required_keys(self):
        csv = "amp\n1\n2\n3\n"
        _, _, meta = load_csv_signal(self._make_file(csv))
        for key in ("source", "n_samples", "sampling_rate_hz", "duration_s"):
            self.assertIn(key, meta)

    def test_nan_values_replaced(self):
        csv = "amplitude\n1.0\nNaN\n3.0\n"
        sig, _, _ = load_csv_signal(self._make_file(csv))
        self.assertFalse(np.any(np.isnan(sig)))

    def test_output_is_float64(self):
        csv = "amplitude\n1\n2\n3\n"
        sig, _, _ = load_csv_signal(self._make_file(csv))
        self.assertEqual(sig.dtype, np.float64)

    def test_source_metadata_value(self):
        csv = "amplitude\n1\n2\n"
        _, _, meta = load_csv_signal(self._make_file(csv))
        self.assertEqual(meta["source"], "CSV upload")


# ─────────────────────────────────────────────────────────────────────────────
# crustal_velocity_at_depth
# ─────────────────────────────────────────────────────────────────────────────

class TestCrustalVelocityAtDepth(unittest.TestCase):

    def test_upper_crust_vp(self):
        vp, _ = crustal_velocity_at_depth(5.0)
        self.assertAlmostEqual(vp, 5.80)

    def test_upper_crust_vs(self):
        _, vs = crustal_velocity_at_depth(5.0)
        self.assertAlmostEqual(vs, 3.36)

    def test_middle_crust(self):
        vp, vs = crustal_velocity_at_depth(20.0)
        self.assertAlmostEqual(vp, 6.50)
        self.assertAlmostEqual(vs, 3.75)

    def test_lower_crust(self):
        vp, vs = crustal_velocity_at_depth(30.0)
        self.assertAlmostEqual(vp, 7.00)
        self.assertAlmostEqual(vs, 4.00)

    def test_upper_mantle(self):
        vp, vs = crustal_velocity_at_depth(100.0)
        self.assertAlmostEqual(vp, 8.04)
        self.assertAlmostEqual(vs, 4.47)

    def test_below_all_layers_returns_mantle(self):
        vp, vs = crustal_velocity_at_depth(500.0)
        self.assertAlmostEqual(vp, 8.04)

    def test_vp_always_greater_than_vs(self):
        for depth in [0, 10, 20, 30, 50, 100, 200]:
            vp, vs = crustal_velocity_at_depth(depth)
            self.assertGreater(vp, vs, f"Vp <= Vs at depth={depth} km")

    def test_returns_tuple_of_two_floats(self):
        result = crustal_velocity_at_depth(15.0)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], float)
        self.assertIsInstance(result[1], float)


# ─────────────────────────────────────────────────────────────────────────────
# travel_time_layered
# ─────────────────────────────────────────────────────────────────────────────

class TestTravelTimeLayered(unittest.TestCase):

    def test_tp_positive(self):
        tp, ts = travel_time_layered(80.0, 10.0)
        self.assertGreater(tp, 0)

    def test_ts_greater_than_tp(self):
        tp, ts = travel_time_layered(80.0, 10.0)
        self.assertGreater(ts, tp)

    def test_sp_delay_positive(self):
        tp, ts = travel_time_layered(80.0, 10.0)
        self.assertGreater(ts - tp, 0)

    def test_travel_time_increases_with_distance(self):
        tp1, _ = travel_time_layered(50.0, 10.0)
        tp2, _ = travel_time_layered(100.0, 10.0)
        self.assertGreater(tp2, tp1)

    def test_sp_delay_scales_with_distance(self):
        _, ts1 = travel_time_layered(50.0, 10.0)
        tp1, _ = travel_time_layered(50.0, 10.0)
        _, ts2 = travel_time_layered(200.0, 10.0)
        tp2, _ = travel_time_layered(200.0, 10.0)
        self.assertGreater(ts2 - tp2, ts1 - tp1)

    def test_wadati_1s_approx_8km(self):
        """Per modello IASP91 crosta superiore: 1 s S-P ≈ 8 km epicentrale."""
        tp, ts = travel_time_layered(8.0, 0.1)
        sp = ts - tp
        self.assertAlmostEqual(sp, 1.0, delta=0.3)

    def test_zero_distance_returns_finite(self):
        tp, ts = travel_time_layered(0.0, 10.0)
        self.assertTrue(np.isfinite(tp))
        self.assertTrue(np.isfinite(ts))


# ─────────────────────────────────────────────────────────────────────────────
# FDSN_PROVIDERS dict
# ─────────────────────────────────────────────────────────────────────────────

class TestFdsnProviders(unittest.TestCase):

    def test_has_five_providers(self):
        self.assertEqual(len(FDSN_PROVIDERS), 5)

    def test_ingv_present(self):
        self.assertTrue(any("INGV" in k for k in FDSN_PROVIDERS))

    def test_iris_present(self):
        self.assertTrue(any("IRIS" in k for k in FDSN_PROVIDERS))

    def test_all_urls_start_with_https(self):
        for name, url in FDSN_PROVIDERS.items():
            self.assertTrue(url.startswith("https://"), f"{name} URL non HTTPS: {url}")

    def test_all_urls_contain_fdsnws(self):
        for name, url in FDSN_PROVIDERS.items():
            self.assertIn("fdsnws", url, f"{name}: URL non FDSN: {url}")


# ─────────────────────────────────────────────────────────────────────────────
# CRUSTAL_LAYERS
# ─────────────────────────────────────────────────────────────────────────────

class TestCrustalLayers(unittest.TestCase):

    def test_four_layers(self):
        self.assertEqual(len(CRUSTAL_LAYERS), 4)

    def test_layers_are_contiguous(self):
        for i in range(len(CRUSTAL_LAYERS) - 1):
            self.assertEqual(CRUSTAL_LAYERS[i][1], CRUSTAL_LAYERS[i + 1][0],
                             "Strati non contigui")

    def test_vp_vs_positive(self):
        for z0, z1, vp, vs, rho in CRUSTAL_LAYERS:
            self.assertGreater(vp, 0)
            self.assertGreater(vs, 0)

    def test_density_realistic(self):
        for z0, z1, vp, vs, rho in CRUSTAL_LAYERS:
            self.assertGreater(rho, 2.0)
            self.assertLess(rho, 5.0)

    def test_vp_increases_with_depth(self):
        vps = [layer[2] for layer in CRUSTAL_LAYERS]
        self.assertEqual(vps, sorted(vps))


# ─────────────────────────────────────────────────────────────────────────────
# fetch_fdsn_waveform — mock HTTP (non richiede rete)
# ─────────────────────────────────────────────────────────────────────────────

class TestFetchFdsnWaveform(unittest.TestCase):

    def _make_fake_mseed_bytes(self) -> "bytes | None":
        """Genera un MiniSEED sintetico minimo usando ObsPy."""
        try:
            from obspy import Trace, Stream
            from obspy.core import UTCDateTime
            tr = Trace(data=np.zeros(100, dtype=np.int32))
            tr.stats.network  = "IV"
            tr.stats.station  = "ACER"
            tr.stats.location = "00"
            tr.stats.channel  = "HHZ"
            tr.stats.sampling_rate = 100.0
            tr.stats.starttime = UTCDateTime("2016-08-24T01:36:00")
            st = Stream([tr])
            buf = io.BytesIO()
            st.write(cast(str, buf), format="MSEED")
            return buf.getvalue()
        except Exception:
            return None

    def test_unknown_provider_raises_valueerror(self):
        with self.assertRaises(ValueError):
            fetch_fdsn_waveform(
                provider_name="UNKNOWN_PROVIDER",
                network="IV", station="ACER", location="00",
                channel="HHZ",
                starttime="2016-08-24T01:36:00",
                endtime="2016-08-24T01:40:00",
            )

    def test_http_404_raises_valueerror(self):
        import urllib.error
        _hdrs = email.message.Message()
        mock_exc = urllib.error.HTTPError(
            url="http://test", code=404, msg="Not Found", hdrs=_hdrs, fp=None
        )
        with patch("urllib.request.urlopen", side_effect=mock_exc):
            with self.assertRaises(ValueError):
                fetch_fdsn_waveform(
                    provider_name="INGV  (Italy)",
                    network="IV", station="XXXX", location="00",
                    channel="HHZ",
                    starttime="2000-01-01T00:00:00",
                    endtime="2000-01-01T00:01:00",
                )

    def test_http_500_raises_connectionerror(self):
        import urllib.error
        _hdrs = email.message.Message()
        mock_exc = urllib.error.HTTPError(
            url="http://test", code=500, msg="Server Error", hdrs=_hdrs, fp=None
        )
        with patch("urllib.request.urlopen", side_effect=mock_exc):
            with self.assertRaises(ConnectionError):
                fetch_fdsn_waveform(
                    provider_name="INGV  (Italy)",
                    network="IV", station="ACER", location="00",
                    channel="HHZ",
                    starttime="2016-08-24T01:36:00",
                    endtime="2016-08-24T01:40:00",
                )

    def test_network_unreachable_raises_connectionerror(self):
        import urllib.error
        mock_exc = urllib.error.URLError(reason="Network unreachable")
        with patch("urllib.request.urlopen", side_effect=mock_exc):
            with self.assertRaises(ConnectionError):
                fetch_fdsn_waveform(
                    provider_name="IRIS  (Global)",
                    network="IU", station="ANMO", location="00",
                    channel="BHZ",
                    starttime="2016-08-24T01:36:00",
                    endtime="2016-08-24T01:40:00",
                )

    def test_successful_fetch_returns_correct_types(self):
        mseed_bytes = self._make_fake_mseed_bytes()
        if mseed_bytes is None:
            self.skipTest("ObsPy non disponibile per generare MiniSEED di test")

        mock_resp = MagicMock()
        mock_resp.read.return_value = mseed_bytes
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            signal, fs, meta = fetch_fdsn_waveform(
                provider_name="INGV  (Italy)",
                network="IV", station="ACER", location="00",
                channel="HHZ",
                starttime="2016-08-24T01:36:00",
                endtime="2016-08-24T01:40:00",
            )

        self.assertIsInstance(signal, np.ndarray)
        self.assertEqual(signal.dtype, np.float64)
        self.assertIsInstance(fs, float)
        self.assertGreater(fs, 0)
        self.assertIsInstance(meta, dict)

    def test_successful_fetch_metadata_keys(self):
        mseed_bytes = self._make_fake_mseed_bytes()
        if mseed_bytes is None:
            self.skipTest("ObsPy non disponibile")

        mock_resp = MagicMock()
        mock_resp.read.return_value = mseed_bytes
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            _, _, meta = fetch_fdsn_waveform(
                provider_name="INGV  (Italy)",
                network="IV", station="ACER", location="00",
                channel="HHZ",
                starttime="2016-08-24T01:36:00",
                endtime="2016-08-24T01:40:00",
            )

        for key in ("source", "network", "station", "channel", "npts",
                    "sampling_rate_hz", "fdsn_url"):
            self.assertIn(key, meta, f"Chiave mancante in metadata: {key}")

    def test_location_double_dash_normalised(self):
        """Location '--' deve essere convertita in stringa vuota nell'URL."""
        mseed_bytes = self._make_fake_mseed_bytes()
        if mseed_bytes is None:
            self.skipTest("ObsPy non disponibile")

        captured_urls = []

        def fake_urlopen(req, timeout=None, **kwargs):
            captured_urls.append(req.full_url)
            mock_resp = MagicMock()
            mock_resp.read.return_value = mseed_bytes
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            return mock_resp

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            fetch_fdsn_waveform(
                provider_name="INGV  (Italy)",
                network="IV", station="ACER", location="--",
                channel="HHZ",
                starttime="2016-08-24T01:36:00",
                endtime="2016-08-24T01:40:00",
            )

        self.assertTrue(len(captured_urls) > 0)
        self.assertIn("location=&", captured_urls[0] + "&")


if __name__ == "__main__":
    unittest.main(verbosity=2)

