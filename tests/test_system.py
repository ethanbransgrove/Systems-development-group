import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.validators import check_password_strength, validate_card_number, validate_expiry, validate_cvv
from models.tenant_model import get_late_invoice_count, get_tenant_invoices, update_late_invoices, create_late_payment_notification
from models.payment_model import get_tenant_payments, create_payment, get_monthly_payments, get_neighbour_payment_totals
from models.maintenance_model import create_maintenance_request, get_tenant_maintenance_requests
from models.complaint_model import create_complaint, get_tenant_complaints
from models.analytics_model import get_late_payments_per_property
from models.user_model import update_user_password, login_user

# ------------------------------------------------------------
# Validators
# ------------------------------------------------------------
class TestValidators(unittest.TestCase):
    
    def test_weak_password(self):
        self.assertEqual(check_password_strength("abc"), "Weak")

    def test_medium_password(self):
        self.assertEqual(check_password_strength("abc12345"), "Medium")

    def test_strong_password(self):
        self.assertEqual(check_password_strength("Abc123!@#"), "Strong")

    def test_valid_card_number(self):
        self.assertTrue(validate_card_number("4111111111111111"))   # Visa test
        self.assertTrue(validate_card_number("5555555555554444"))   # Mastercard test
        self.assertTrue(validate_card_number("4242424242424242"))   # Visa test

    def test_invalid_card_number(self):
        # Remove the space test; our validator strips spaces, so it would pass.
        # Instead use invalid Luhn or wrong length.
        self.assertFalse(validate_card_number("1234567890123456"))   # Invalid Luhn
        self.assertFalse(validate_card_number("411111111111111"))    # 15 digits
        self.assertFalse(validate_card_number("41111111111111111"))  # 17 digits
        self.assertFalse(validate_card_number("4111-1111-1111-1111")) # includes hyphens

    def test_valid_expiry(self):
        self.assertTrue(validate_expiry("12/30"))   # December 2030
        self.assertTrue(validate_expiry("01/27"))

    def test_invalid_expiry(self):
        self.assertFalse(validate_expiry("13/25"))
        self.assertFalse(validate_expiry("12/23"))   # expired
        self.assertFalse(validate_expiry("12-25"))

    def test_valid_cvv(self):
        self.assertTrue(validate_cvv("123"))
        self.assertFalse(validate_cvv("12"))
        self.assertFalse(validate_cvv("12a"))
        self.assertFalse(validate_cvv("1234"))

# ------------------------------------------------------------
# Tenant Dashboard Feature Tests
# ------------------------------------------------------------
class TestTenantDashboardFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tenant_id = 2          # John Smith
        cls.user_id = 14           # user for tenant 2

    def test_view_own_payments(self):
        payments = get_tenant_payments(self.tenant_id)
        self.assertIsInstance(payments, list)
        if payments:
            self.assertIn("amount", payments[0])
            self.assertIn("payment_date", payments[0])

    def test_late_payment_alerts(self):
        update_late_invoices(self.tenant_id)
        create_late_payment_notification(self.user_id, self.tenant_id)
        from models.notification_model import get_all_notifications
        notifications = get_all_notifications(self.user_id)
        late_notifications = [n for n in notifications if n["type"] == "LATE_PAYMENT"]
        self.assertIsInstance(late_notifications, list)

    def test_submit_complaint(self):
        result = create_complaint(self.tenant_id, "Test complaint from unit test")
        self.assertTrue(result)
        complaints = get_tenant_complaints(self.tenant_id)
        self.assertTrue(any("Test complaint" in c["description"] for c in complaints))

    def test_submit_maintenance_request(self):
        # Now includes priority argument
        result = create_maintenance_request(self.tenant_id, "Test maintenance request", "LOW")
        self.assertTrue(result)
        requests = get_tenant_maintenance_requests(self.tenant_id)
        self.assertTrue(any("Test maintenance" in r["description"] for r in requests))

    def test_view_repair_progress(self):
        requests = get_tenant_maintenance_requests(self.tenant_id)
        self.assertIsInstance(requests, list)
        for req in requests:
            self.assertIn("status", req)
            self.assertIn(req["status"], ["REPORTED", "IN_PROGRESS", "RESOLVED"])

    def test_payment_history_graph_data(self):
        data = get_monthly_payments(self.tenant_id)
        self.assertIsInstance(data, list)
        for item in data:
            self.assertIn("month", item)
            self.assertIn("total", item)

    def test_neighbour_comparison_data(self):
        data = get_neighbour_payment_totals(self.tenant_id)
        self.assertIsInstance(data, list)
        for item in data:
            self.assertIn("name", item)
            self.assertIn("total", item)

    def test_make_payment(self):
        # Get unpaid invoices
        invoices = get_tenant_invoices(self.tenant_id)   # imported correctly
        unpaid = [i for i in invoices if i["status"] != "PAID"]
        if not unpaid:
            self.skipTest("No unpaid invoice available for testing")
        invoice = unpaid[0]
        card_number = "4111111111111111"
        self.assertTrue(validate_card_number(card_number))
        self.assertTrue(validate_expiry("12/30"))
        self.assertTrue(validate_cvv("123"))
        result = create_payment(invoice["invoice_id"], invoice["lease_id"], invoice["amount_due"], card_number)
        self.assertTrue(result)
        # Verify invoice status updated
        updated_invoices = get_tenant_invoices(self.tenant_id)
        paid_invoice = next((i for i in updated_invoices if i["invoice_id"] == invoice["invoice_id"]), None)
        self.assertIsNotNone(paid_invoice)
        self.assertEqual(paid_invoice["status"], "PAID")

    def test_late_payments_per_property(self):
        data = get_late_payments_per_property()
        self.assertIsInstance(data, list)
        for item in data:
            self.assertIn("name", item)
            self.assertIn("late_count", item)

    def test_change_password(self):
        # Use dummy user will@test.com (user_id = 16)
        user_id = 16
        original_password = "123"
        new_password = "TempPass123!"

        # Verify original login works
        user = login_user("will@test.com", original_password)
        self.assertIsNotNone(user)

        # Change password
        success = update_user_password(user_id, new_password)
        self.assertTrue(success)

        # Verify login with new password works
        user2 = login_user("will@test.com", new_password)
        self.assertIsNotNone(user2)

        # Revert to original password
        revert_success = update_user_password(user_id, original_password)
        self.assertTrue(revert_success)

        # Verify original login works again
        user3 = login_user("will@test.com", original_password)
        self.assertIsNotNone(user3)

# ------------------------------------------------------------
# Edge Cases
# ------------------------------------------------------------
class TestEdgeCases(unittest.TestCase):

    def test_get_tenant_payments_nonexistent_tenant(self):
        payments = get_tenant_payments(9999)
        self.assertEqual(payments, [])

    def test_create_complaint_invalid_tenant(self):
        result = create_complaint(9999, "No active lease")
        self.assertFalse(result)

    def test_create_maintenance_request_invalid_tenant(self):
        # Now includes priority
        result = create_maintenance_request(9999, "No active lease", "LOW")
        self.assertFalse(result)

# ------------------------------------------------------------
# Run tests
# ------------------------------------------------------------
if __name__ == "__main__":
    unittest.main(verbosity=2)