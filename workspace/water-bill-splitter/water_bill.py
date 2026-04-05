#!/usr/bin/env python3
"""
Water Bill Splitter for Shared Housing
Calculates A and B shares based on meter readings and fixed fees
"""

def calculate_water_bill(
    meter_a_current,
    meter_a_previous,
    meter_b_current,
    meter_b_previous,
    water_charge,
    wastewater_charge,
    basic_fee_water,
    basic_fee_wastewater
):
    """Calculate A and B shares for water bill"""
    
    # Calculate consumption
    consumption_a = meter_a_current - meter_a_previous
    consumption_b = meter_b_current - meter_b_previous
    total_consumption = consumption_a + consumption_b
    
    if total_consumption == 0:
        return None, "No consumption recorded"
    
    # Calculate percentages
    pct_a = consumption_a / total_consumption
    pct_b = consumption_b / total_consumption
    
    # Calculate shares
    # Basic fees are split 50/50
    basic_fee_a = (basic_fee_water + basic_fee_wastewater) / 2
    basic_fee_b = (basic_fee_water + basic_fee_wastewater) / 2
    
    # Consumption-based charges split by percentage
    water_a = water_charge * pct_a
    water_b = water_charge * pct_b
    
    wastewater_a = wastewater_charge * pct_a
    wastewater_b = wastewater_charge * pct_b
    
    # Totals
    total_a = basic_fee_a + water_a + wastewater_a
    total_b = basic_fee_b + water_b + wastewater_b
    
    return {
        "consumption_a": consumption_a,
        "consumption_b": consumption_b,
        "total_consumption": total_consumption,
        "pct_a": round(pct_a * 100, 1),
        "pct_b": round(pct_b * 100, 1),
        "basic_fee_a": round(basic_fee_a, 2),
        "basic_fee_b": round(basic_fee_b, 2),
        "water_a": round(water_a, 2),
        "water_b": round(water_b, 2),
        "wastewater_a": round(wastewater_a, 2),
        "wastewater_b": round(wastewater_b, 2),
        "total_a": round(total_a, 2),
        "total_b": round(total_b, 2)
    }


def print_result(result):
    """Print the calculation results"""
    print("=" * 50)
    print("VESILASKUN JAKO / WATER BILL SPLIT")
    print("=" * 50)
    print(f"\nKulutus / Consumption:")
    print(f"  A: {result['consumption_a']} m³ ({result['pct_a']}%)")
    print(f"  B: {result['consumption_b']} m³ ({result['pct_b']}%)")
    print(f"  Yht: {result['total_consumption']} m³")
    
    print(f"\nPerusmaksut (50/50) / Basic Fees:")
    print(f"  A: {result['basic_fee_a']:.2f} €")
    print(f"  B: {result['basic_fee_b']:.2f} €")
    
    print(f"\nVesi (kulutuksen mukaan) / Water:")
    print(f"  A: {result['water_a']:.2f} €")
    print(f"  B: {result['water_b']:.2f} €")
    
    print(f"\nJätevesi (kulutuksen mukaan) / Wastewater:")
    print(f"  A: {result['wastewater_a']:.2f} €")
    print(f"  B: {result['wastewater_b']:.2f} €")
    
    print(f"\n{'=' * 50}")
    print(f"YHTENSÄ / TOTAL:")
    print(f"  A: {result['total_a']:.2f} €")
    print(f"  B: {result['total_b']:.2f} €")
    print(f"{'=' * 50}")


# Example usage - update these values for each bill
if __name__ == "__main__":
    # UPDATE THESE VALUES FOR EACH BILL
    METER_A_CURRENT = 668      # Current reading A
    METER_A_PREVIOUS = 653     # Previous reading A
    METER_B_CURRENT = 1053     # Current reading B  
    METER_B_PREVIOUS = 1030    # Previous reading B
    
    # From the bill - update these too
    WATER_CHARGE = 92.62        # Water charge (€)
    WASTEWATER_CHARGE = 158.13 # Wastewater charge (€)
    BASIC_FEE_WATER = 18.98    # Water basic fee (€)
    BASIC_FEE_WASTEWATER = 24.17 # Wastewater basic fee (€)
    
    result = calculate_water_bill(
        METER_A_CURRENT, METER_A_PREVIOUS,
        METER_B_CURRENT, METER_B_PREVIOUS,
        WATER_CHARGE, WASTEWATER_CHARGE,
        BASIC_FEE_WATER, BASIC_FEE_WASTEWATER
    )
    
    print_result(result)