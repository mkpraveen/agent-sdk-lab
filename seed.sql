PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

INSERT OR IGNORE INTO invoice_header (
  invoice_id, invoice_number, customer_id, invoice_date, due_date,
  currency_code, status, subtotal_amount, tax_amount, total_amount, notes
) VALUES
  (1, 'INV-2026-0001', 1001, '2026-01-05', '2026-02-04', 'USD', 'issued', 215.00, 13.60, 228.60, 'Office setup'),
  (2, 'INV-2026-0002', 1002, '2026-01-08', '2026-02-07', 'USD', 'issued', 106.00, 2.88, 108.88, 'Cables and stand'),
  (3, 'INV-2026-0003', 1003, '2026-01-12', '2026-02-11', 'USD', 'paid',   267.00, 18.80, 285.80, 'Storage upgrade'),
  (4, 'INV-2026-0004', 1004, '2026-01-15', '2026-02-14', 'USD', 'issued', 140.00, 4.80, 144.80, 'Ergonomics'),
  (5, 'INV-2026-0005', 1005, '2026-01-18', '2026-02-17', 'USD', 'issued', 334.00, 26.24, 360.24, 'Monitor bundle'),
  (6, 'INV-2026-0006', 1006, '2026-01-21', '2026-02-20', 'USD', 'paid',   119.00, 7.60, 126.60, 'Audio gear'),
  (7, 'INV-2026-0007', 1007, '2026-01-25', '2026-02-24', 'USD', 'issued', 253.00, 5.84, 258.84, 'Docking kit'),
  (8, 'INV-2026-0008', 1008, '2026-01-28', '2026-02-27', 'USD', 'issued', 185.00, 14.80, 199.80, 'Video upgrade');

INSERT OR IGNORE INTO invoice_line (
  line_id, invoice_id, line_number, item_code, description,
  quantity, unit_price, discount_amount, tax_amount, line_total
) VALUES
  (1, 1, 1, 'MOUSE-WL', 'Wireless Mouse', 2, 25.00, 0.00, 4.00, 54.00),
  (2, 1, 2, 'KB-MECH', 'Mechanical Keyboard', 1, 120.00, 0.00, 9.60, 129.60),
  (3, 1, 3, 'HUB-USBC', 'USB-C Hub', 1, 45.00, 0.00, 0.00, 45.00),

  (4, 2, 1, 'STAND-LAP', 'Laptop Stand', 2, 35.00, 0.00, 0.00, 70.00),
  (5, 2, 2, 'HDMI-2M', 'HDMI Cable 2m', 3, 12.00, 0.00, 2.88, 38.88),

  (6, 3, 1, 'SSD-1TB', 'External SSD 1TB', 1, 160.00, 0.00, 12.80, 172.80),
  (7, 3, 2, 'ADAPT-UC', 'USB-A to USB-C Adapter', 4, 8.00, 0.00, 0.00, 32.00),
  (8, 3, 3, 'WEBCAM-1080', 'Webcam 1080p', 1, 75.00, 0.00, 6.00, 81.00),

  (9, 4, 1, 'KB-WL', 'Wireless Keyboard', 1, 80.00, 0.00, 0.00, 80.00),
  (10, 4, 2, 'MOUSE-ERG', 'Ergonomic Mouse', 1, 60.00, 0.00, 4.80, 64.80),

  (11, 5, 1, 'MON-24', 'Monitor 24in', 2, 150.00, 0.00, 24.00, 324.00),
  (12, 5, 2, 'DPORT-2M', 'DisplayPort Cable', 2, 14.00, 0.00, 2.24, 30.24),
  (13, 5, 3, 'TIES-PACK', 'Cable Ties Pack', 1, 6.00, 0.00, 0.00, 6.00),

  (14, 6, 1, 'HEADSET-G', 'Gaming Headset', 1, 95.00, 0.00, 7.60, 102.60),
  (15, 6, 2, 'PAD-L', 'Mouse Pad', 2, 12.00, 0.00, 0.00, 24.00),

  (16, 7, 1, 'DOCK-USB', 'Docking Station', 1, 180.00, 0.00, 0.00, 180.00),
  (17, 7, 2, 'ETH-2M', 'Ethernet Cable', 4, 7.00, 0.00, 2.24, 30.24),
  (18, 7, 3, 'CHG-65W', 'USB-C Charger 65W', 1, 45.00, 0.00, 3.60, 48.60),

  (19, 8, 1, 'SPKR-BT', 'Bluetooth Speaker', 1, 55.00, 0.00, 4.40, 59.40),
  (20, 8, 2, 'WEBCAM-4K', 'Webcam 4K', 1, 130.00, 0.00, 10.40, 140.40);

INSERT OR IGNORE INTO customer_master (
  customer_id, customer_name, email, phone,
  billing_address1, billing_address2, city, state, postal_code, country
) VALUES
  (1001, 'Northwind Office Supply', 'ap@northwind.example', '206-555-0101', '1200 Aurora Ave', 'Suite 210', 'Seattle', 'WA', '98101', 'USA'),
  (1002, 'Pioneer Tech Co.', 'billing@pioneer.example', '503-555-0134', '455 SW Morrison St', NULL, 'Portland', 'OR', '97204', 'USA'),
  (1003, 'Blue Ridge Analytics', 'accounts@blueridge.example', '303-555-0199', '820 Market St', 'Floor 5', 'Denver', 'CO', '80202', 'USA'),
  (1004, 'Lakeside Media Group', 'finance@lakeside.example', '312-555-0145', '233 W Madison St', NULL, 'Chicago', 'IL', '60606', 'USA'),
  (1005, 'Desert Ridge Labs', 'billing@desertridge.example', '480-555-0118', '900 E Camelback Rd', 'Bldg C', 'Phoenix', 'AZ', '85012', 'USA'),
  (1006, 'Crescent City Design', 'ap@crescentcity.example', '504-555-0176', '510 Magazine St', NULL, 'New Orleans', 'LA', '70130', 'USA'),
  (1007, 'Great Plains Freight', 'billing@greatplains.example', '402-555-0162', '715 Farnam St', 'Suite 400', 'Omaha', 'NE', '68102', 'USA'),
  (1008, 'Bayview Creative Studio', 'ap@bayview.example', '415-555-0183', '250 Montgomery St', 'Suite 900', 'San Francisco', 'CA', '94104', 'USA');

COMMIT;
