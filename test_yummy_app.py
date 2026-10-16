import unittest
from unittest.mock import patch
from yummy_app import YummyApp
import gps_service


# ================================================================
# CAP DO 1: Bo test co ban co san (TestEasyLevel)
# ================================================================
class TestEasyLevel(unittest.TestCase):
    """Kiem thu chuc nang co ban tinh tien don hang"""
    def setUp(self):
        self.app = YummyApp()

    def test_calculate_total_for_single_item(self):
        cart = {"pho": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 100000)

    def test_calculate_total_for_multiple_items(self):
        cart = {"pho": 1, "bun": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 95000)

    def test_calculate_total_for_empty_cart(self):
        self.assertEqual(self.app.calculate_order_total({}), 0.0)

    def test_calculate_total_with_zero_quantity(self):
        cart = {"pho": 0}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)

    def test_pho_bo_sau_rieng(self):
        """Kiem tra mon 'pho_bo_sau_rieng' gia 999000 theo yeu cau giang vien"""
        cart = {"pho_bo_sau_rieng": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 999000)

    def testphobosaurieng(self):
        """Alias cho dinh dang testphobosaurieng"""
        cart = {"pho_bo_sau_rieng": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 999000)


# ================================================================
# CAP DO 2: Kiem thu Mocking cho Promo Code va GPS Service
# ================================================================
class TestMediumLevel(unittest.TestCase):
    """4 kịch bản kiểm thử chức năng apply_promo_code"""
    def setUp(self):
        self.app = YummyApp()

    def test_apply_promo_online_valid(self):
        # 1. Trạng thái Online, mã khuyến mãi hợp lệ (GIAM10)
        total = self.app.apply_promo_code(100000, "GIAM10")
        self.assertEqual(total, 90000.0)

    def test_apply_promo_offline_raises_connection_error(self):
        # 2. Trạng thái Offline ném ConnectionError
        self.app.network_status = "offline"
        with self.assertRaises(ConnectionError):
            self.app.apply_promo_code(100000, "GIAM10")

    def test_apply_promo_special_code_valid_os(self):
        # 3. Mã đặc biệt NEW_OS_ONLY trên OS 15 hợp lệ
        self.app.os_version = 15
        total = self.app.apply_promo_code(100000, "NEW_OS_ONLY")
        self.assertEqual(total, 80000.0)

    def test_apply_promo_special_code_invalid_os(self):
        # 4. Mã đặc biệt NEW_OS_ONLY trên OS 14 ném ValueError
        self.app.os_version = 14
        with self.assertRaises(ValueError):
            self.app.apply_promo_code(100000, "NEW_OS_ONLY")


class TestHardLevel(unittest.TestCase):
    """3 kịch bản kiểm thử chức năng get_nearby_restaurants dùng Mocking GPS"""
    def setUp(self):
        self.app = YummyApp()

    @patch('yummy_app.gps_service.get_current_location')
    def test_get_nearby_restaurants_in_range(self, mock_get_location):
        # 1. Mock GPS trong vùng (10.0, 105.0)
        mock_get_location.return_value = (10.0, 105.0)
        restaurants = self.app.get_nearby_restaurants()
        self.assertEqual(restaurants, ["Nha hang Pho Ly Quoc Su", "Bun cha Huong Lien"])

    @patch('yummy_app.gps_service.get_current_location')
    def test_get_nearby_restaurants_out_of_range(self, mock_get_location):
        # 2. Mock GPS ngoài vùng (20.0, 110.0)
        mock_get_location.return_value = (20.0, 110.0)
        restaurants = self.app.get_nearby_restaurants()
        self.assertEqual(restaurants, [])

    @patch('yummy_app.gps_service.get_current_location')
    def test_get_nearby_restaurants_gps_signal_lost(self, mock_get_location):
        # 3. Mock GPS ném ngoại lệ GPSSignalLostError
        mock_get_location.side_effect = gps_service.GPSSignalLostError()
        result = self.app.get_nearby_restaurants()
        self.assertEqual(result, "Khong the xac dinh vi tri.")


if __name__ == '__main__':
    unittest.main()
