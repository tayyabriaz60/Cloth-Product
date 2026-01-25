"""
Comprehensive Test Suite for Billing System Calculations
Tests all mathematical calculations and business logic
"""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from main import app, Inventory, SalesRecord, SessionLocal, engine, Base
from sqlalchemy.orm import sessionmaker

# Create test client - will be created per test to avoid initialization issues
@pytest.fixture(scope="function")
def client():
    """Create a test client"""
    return TestClient(app)

# Test database setup
@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    # Clean up test data
    with engine.begin() as conn:
        conn.execute(Base.metadata.tables['sales_records'].delete())
        conn.execute(Base.metadata.tables['inventory'].delete())


class TestStockCalculations:
    """Test stock addition and update calculations"""
    
    def test_add_stock_calculation(self, db_session, client):
        """Test: total_meters = total_thans * meters_per_than"""
        # Test Case 1: Standard values
        stock_data = {
            "company_name": "Gul Ahmed",
            "design_code": "D-101",
            "total_thans": 5.0,
            "meters_per_than": 20.0,
            "cost_price_per_meter": 100.0
        }
        
        response = client.post("/add-stock", json=stock_data)
        assert response.status_code == 200
        
        data = response.json()
        expected_total_meters = Decimal('5.0') * Decimal('20.0')  # 100.0
        expected_stock_value = expected_total_meters * Decimal('100.0')  # 10000.0
        
        # Handle string conversion from Pydantic Decimal serialization
        total_meters = float(data['total_meters']) if isinstance(data['total_meters'], str) else data['total_meters']
        total_stock_value = float(data['total_stock_value']) if isinstance(data['total_stock_value'], str) else data['total_stock_value']
        
        assert abs(total_meters - float(expected_total_meters)) < 0.01
        assert abs(total_stock_value - float(expected_stock_value)) < 0.01
        assert total_meters == 100.0
        assert abs(total_stock_value - 10000.0) < 0.01
    
    def test_add_stock_decimal_precision(self, db_session, client):
        """Test: Decimal precision handling"""
        stock_data = {
            "company_name": "Test Company",
            "design_code": "D-102",
            "total_thans": 3.5,
            "meters_per_than": 25.5,
            "cost_price_per_meter": 150.75
        }
        
        response = client.post("/add-stock", json=stock_data)
        assert response.status_code == 200
        
        data = response.json()
        expected_total_meters = 3.5 * 25.5  # 89.25
        expected_stock_value = expected_total_meters * 150.75  # 13454.4375
        
        assert abs(float(data['total_meters']) - expected_total_meters) < 0.01
        assert abs(float(data['total_stock_value']) - expected_stock_value) < 0.01
    
    def test_update_stock_recalculation(self, db_session, client):
        """Test: Stock update recalculates total_meters and total_stock_value"""
        # First add stock
        stock_data = {
            "company_name": "Test Company",
            "design_code": "D-103",
            "total_thans": 5.0,
            "meters_per_than": 20.0,
            "cost_price_per_meter": 100.0
        }
        response = client.post("/add-stock", json=stock_data)
        stock_id = response.json()['id']
        
        # Update stock
        update_data = {
            "total_thans": 10.0,
            "meters_per_than": 25.0,
            "cost_price_per_meter": 120.0
        }
        response = client.put(f"/update-stock/{stock_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        expected_total_meters = 10.0 * 25.0  # 250.0
        expected_stock_value = expected_total_meters * 120.0  # 30000.0
        
        assert float(data['total_meters']) == expected_total_meters
        assert float(data['total_stock_value']) == expected_stock_value


class TestBillCalculations:
    """Test bill creation calculations"""
    
    def test_bill_totals_calculation(self, db_session, client):
        """Test: kameez_total, shalwar_total, grand_total"""
        # Add stock first
        stock_data = {
            "company_name": "Gul Ahmed",
            "design_code": "D-101",
            "total_thans": 10.0,
            "meters_per_than": 20.0,
            "cost_price_per_meter": 100.0
        }
        stock_response = client.post("/add-stock", json=stock_data)
        stock_id = stock_response.json()['id']
        
        # Create bill
        bill_data = {
            "kameez_inventory_id": stock_id,
            "shalwar_inventory_id": stock_id,
            "kameez_meters": 2.5,
            "kameez_rate": 200.0,
            "shalwar_meters": 2.5,
            "shalwar_rate": 180.0
        }
        
        response = client.post("/create-bill", json=bill_data)
        assert response.status_code == 200
        
        data = response.json()
        expected_kameez_total = 2.5 * 200.0  # 500.0
        expected_shalwar_total = 2.5 * 180.0  # 450.0
        expected_grand_total = expected_kameez_total + expected_shalwar_total  # 950.0
        
        assert abs(float(data['kameez_total']) - expected_kameez_total) < 0.01
        assert abs(float(data['shalwar_total']) - expected_shalwar_total) < 0.01
        assert abs(float(data['grand_total']) - expected_grand_total) < 0.01
    
    def test_bill_zero_values(self, db_session, client):
        """Test: Handling zero values"""
        stock_data = {
            "company_name": "Test Company",
            "design_code": "D-102",
            "total_thans": 10.0,
            "meters_per_than": 20.0,
            "cost_price_per_meter": 100.0
        }
        stock_response = client.post("/add-stock", json=stock_data)
        stock_id = stock_response.json()['id']
        
        bill_data = {
            "kameez_inventory_id": stock_id,
            "kameez_meters": 0.0,
            "kameez_rate": 200.0,
            "shalwar_meters": 2.5,
            "shalwar_rate": 180.0
        }
        
        response = client.post("/create-bill", json=bill_data)
        assert response.status_code == 200
        
        data = response.json()
        assert float(data['kameez_total']) == 0.0
        assert float(data['grand_total']) == float(data['shalwar_total'])


class TestInventoryStatusCalculations:
    """Test inventory status calculations"""
    
    def test_remaining_meters_calculation(self, db_session, client):
        """Test: remaining_meters = total_meters - sold_meters"""
        # Add stock
        stock_data = {
            "company_name": "Gul Ahmed",
            "design_code": "D-101",
            "total_thans": 5.0,
            "meters_per_than": 20.0,
            "cost_price_per_meter": 100.0
        }
        stock_response = client.post("/add-stock", json=stock_data)
        stock_id = stock_response.json()['id']
        
        # Create sale
        bill_data = {
            "kameez_inventory_id": stock_id,
            "shalwar_inventory_id": stock_id,
            "kameez_meters": 2.5,
            "kameez_rate": 200.0,
            "shalwar_meters": 2.5,
            "shalwar_rate": 180.0
        }
        client.post("/create-bill", json=bill_data)
        
        # Check inventory status
        response = client.get("/get-inventory")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        item = data[0]
        total_meters = float(item['total_meters'])  # 100.0
        sold_meters = float(item['sold_meters'])  # 5.0 (2.5 + 2.5)
        remaining_meters = float(item['remaining_meters'])  # 95.0
        
        assert sold_meters == 5.0
        assert remaining_meters == total_meters - sold_meters
        assert remaining_meters == 95.0
    
    def test_remaining_stock_value_calculation(self, db_session, client):
        """Test: remaining_stock_value = remaining_meters * cost_price_per_meter"""
        stock_data = {
            "company_name": "Test Company",
            "design_code": "D-102",
            "total_thans": 10.0,
            "meters_per_than": 20.0,
            "cost_price_per_meter": 150.0
        }
        stock_response = client.post("/add-stock", json=stock_data)
        stock_id = stock_response.json()['id']
        
        # Sell 5 meters
        bill_data = {
            "kameez_inventory_id": stock_id,
            "kameez_meters": 5.0,
            "kameez_rate": 200.0,
            "shalwar_meters": 0.0,
            "shalwar_rate": 0.0
        }
        client.post("/create-bill", json=bill_data)
        
        response = client.get("/get-inventory")
        item = response.json()[0]
        
        remaining_meters = float(item['remaining_meters'])  # 195.0
        cost_per_meter = float(item['cost_price_per_meter'])  # 150.0
        remaining_stock_value = float(item['remaining_stock_value'])  # 29250.0
        
        expected_value = remaining_meters * cost_per_meter
        assert abs(remaining_stock_value - expected_value) < 0.01


class TestProfitLossCalculations:
    """Test profit/loss calculations"""
    
    def test_profit_calculation_new_method(self, db_session, client):
        """Test: profit = revenue - cost for new method (separate inventory)"""
        # Add stock
        stock_data = {
            "company_name": "Gul Ahmed",
            "design_code": "D-101",
            "total_thans": 10.0,
            "meters_per_than": 20.0,
            "cost_price_per_meter": 100.0
        }
        stock_response = client.post("/add-stock", json=stock_data)
        stock_id = stock_response.json()['id']
        
        # Create sale: 5 meters at 200 per meter
        bill_data = {
            "kameez_inventory_id": stock_id,
            "kameez_meters": 5.0,
            "kameez_rate": 200.0,
            "shalwar_meters": 0.0,
            "shalwar_rate": 0.0
        }
        client.post("/create-bill", json=bill_data)
        
        # Get profit/loss
        response = client.get("/get-profit-loss")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        item = data[0]
        meters_sold = float(item['meters_sold'])  # 5.0
        cost_per_meter = float(item['cost_price_per_meter'])  # 100.0
        total_cost = float(item['total_cost'])  # 500.0
        total_revenue = float(item['total_revenue'])  # 1000.0 (5 * 200)
        profit = float(item['profit'])  # 500.0
        profit_percentage = float(item['profit_percentage'])  # 100.0%
        
        assert meters_sold == 5.0
        assert total_cost == meters_sold * cost_per_meter
        assert total_revenue == 5.0 * 200.0
        assert profit == total_revenue - total_cost
        assert abs(profit_percentage - (profit / total_cost * 100)) < 0.01
    
    def test_profit_calculation_old_method(self, db_session, client):
        """Test: profit calculation for old method (inventory_id)"""
        stock_data = {
            "company_name": "Test Company",
            "design_code": "D-102",
            "total_thans": 10.0,
            "meters_per_than": 20.0,
            "cost_price_per_meter": 100.0
        }
        stock_response = client.post("/add-stock", json=stock_data)
        stock_id = stock_response.json()['id']
        
        # Create sale using old method
        bill_data = {
            "inventory_id": stock_id,
            "kameez_meters": 2.5,
            "kameez_rate": 200.0,
            "shalwar_meters": 2.5,
            "shalwar_rate": 180.0
        }
        client.post("/create-bill", json=bill_data)
        
        response = client.get("/get-profit-loss")
        data = response.json()
        
        item = data[0]
        meters_sold = float(item['meters_sold'])  # 5.0 (2.5 + 2.5)
        total_cost = float(item['total_cost'])  # 500.0 (5 * 100)
        total_revenue = float(item['total_revenue'])  # 950.0 (grand_total)
        profit = float(item['profit'])  # 450.0
        
        assert meters_sold == 5.0
        assert total_cost == 500.0
        assert total_revenue == 950.0
        assert profit == 450.0
    
    def test_profit_percentage_calculation(self, db_session, client):
        """Test: profit_percentage = (profit / total_cost) * 100"""
        stock_data = {
            "company_name": "Test Company",
            "design_code": "D-103",
            "total_thans": 10.0,
            "meters_per_than": 20.0,
            "cost_price_per_meter": 100.0
        }
        stock_response = client.post("/add-stock", json=stock_data)
        stock_id = stock_response.json()['id']
        
        # Sell at 50% markup
        bill_data = {
            "kameez_inventory_id": stock_id,
            "kameez_meters": 10.0,
            "kameez_rate": 150.0,  # 50% markup
            "shalwar_meters": 0.0,
            "shalwar_rate": 0.0
        }
        client.post("/create-bill", json=bill_data)
        
        response = client.get("/get-profit-loss")
        data = response.json()
        
        item = data[0]
        total_cost = float(item['total_cost'])  # 1000.0
        total_revenue = float(item['total_revenue'])  # 1500.0
        profit = float(item['profit'])  # 500.0
        profit_percentage = float(item['profit_percentage'])  # 50.0%
        
        expected_percentage = (profit / total_cost) * 100
        assert abs(profit_percentage - expected_percentage) < 0.01
        assert profit_percentage == 50.0


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_large_numbers(self, db_session, client):
        """Test: Large number calculations"""
        stock_data = {
            "company_name": "Test Company",
            "design_code": "D-104",
            "total_thans": 1000.0,
            "meters_per_than": 25.0,
            "cost_price_per_meter": 500.0
        }
        response = client.post("/add-stock", json=stock_data)
        assert response.status_code == 200
        
        data = response.json()
        assert float(data['total_meters']) == 25000.0
        assert float(data['total_stock_value']) == 12500000.0
    
    def test_small_decimal_values(self, db_session, client):
        """Test: Small decimal precision"""
        stock_data = {
            "company_name": "Test Company",
            "design_code": "D-105",
            "total_thans": 0.01,
            "meters_per_than": 0.5,
            "cost_price_per_meter": 0.25
        }
        response = client.post("/add-stock", json=stock_data)
        assert response.status_code == 200
        
        data = response.json()
        # Use Decimal for precise calculation (same as backend)
        expected_meters = Decimal('0.01') * Decimal('0.5')  # 0.005
        expected_value = expected_meters * Decimal('0.25')  # 0.00125
        
        # Handle string conversion from Pydantic Decimal serialization
        total_meters = float(data['total_meters']) if isinstance(data['total_meters'], str) else data['total_meters']
        total_stock_value = float(data['total_stock_value']) if isinstance(data['total_stock_value'], str) else data['total_stock_value']
        
        # Check if calculation matches (with tolerance for floating point precision)
        assert abs(total_meters - float(expected_meters)) < 0.001, f"Expected ~{expected_meters}, got {total_meters}"
        assert abs(total_stock_value - float(expected_value)) < 0.001, f"Expected ~{expected_value}, got {total_stock_value}"
    
    def test_multiple_sales_same_inventory(self, db_session, client):
        """Test: Multiple sales from same inventory"""
        stock_data = {
            "company_name": "Test Company",
            "design_code": "D-106",
            "total_thans": 10.0,
            "meters_per_than": 20.0,
            "cost_price_per_meter": 100.0
        }
        stock_response = client.post("/add-stock", json=stock_data)
        stock_id = stock_response.json()['id']
        
        # Make 3 sales
        for i in range(3):
            bill_data = {
                "kameez_inventory_id": stock_id,
                "kameez_meters": 5.0,
                "kameez_rate": 200.0,
                "shalwar_meters": 0.0,
                "shalwar_rate": 0.0
            }
            client.post("/create-bill", json=bill_data)
        
        response = client.get("/get-inventory")
        item = response.json()[0]
        
        total_meters = float(item['total_meters'])  # 200.0
        sold_meters = float(item['sold_meters'])  # 15.0 (3 * 5)
        remaining_meters = float(item['remaining_meters'])  # 185.0
        
        assert sold_meters == 15.0
        assert remaining_meters == total_meters - sold_meters


class TestStockValidation:
    """Test stock validation logic"""
    
    def test_insufficient_stock_error(self, db_session, client):
        """Test: Error when trying to sell more than available"""
        stock_data = {
            "company_name": "Test Company",
            "design_code": "D-107",
            "total_thans": 5.0,
            "meters_per_than": 20.0,
            "cost_price_per_meter": 100.0
        }
        stock_response = client.post("/add-stock", json=stock_data)
        stock_id = stock_response.json()['id']
        
        # Try to sell more than available (100 meters available, trying to sell 101)
        bill_data = {
            "kameez_inventory_id": stock_id,
            "kameez_meters": 101.0,
            "kameez_rate": 200.0,
            "shalwar_meters": 0.0,
            "shalwar_rate": 0.0
        }
        
        response = client.post("/create-bill", json=bill_data)
        assert response.status_code == 400
        assert "Insufficient stock" in response.json()['detail']


if __name__ == "__main__":
    print("Running comprehensive calculation tests...")
    print("\n" + "="*60)
    print("Test Summary:")
    print("="*60)
    print("✓ Stock Calculations: total_meters, total_stock_value")
    print("✓ Bill Calculations: kameez_total, shalwar_total, grand_total")
    print("✓ Inventory Status: remaining_meters, remaining_stock_value")
    print("✓ Profit/Loss: profit, profit_percentage")
    print("✓ Edge Cases: Large numbers, small decimals, multiple sales")
    print("✓ Validation: Insufficient stock errors")
    print("\nTo run tests: pytest test_calculations.py -v")
