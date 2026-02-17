# phase_5_business/impact_calculator.py

KWH_PRICE_RS = 5  # ₹5 per kWh
HOURS_PER_DAY = 8  # average solar productive hours
DAYS_PER_YEAR = 365


def calculate_energy_loss_kwh(power_loss_watts):
    """
    Convert instantaneous power loss (W) to daily kWh loss.
    """
    # Convert watts to kW
    loss_kw = power_loss_watts / 1000

    # Daily energy loss
    daily_kwh_loss = loss_kw * HOURS_PER_DAY

    return daily_kwh_loss


def calculate_annual_revenue_loss(power_loss_watts):
    """
    Estimate yearly revenue loss in ₹.
    """
    daily_kwh_loss = calculate_energy_loss_kwh(power_loss_watts)

    annual_kwh_loss = daily_kwh_loss * DAYS_PER_YEAR

    annual_revenue_loss = annual_kwh_loss * KWH_PRICE_RS

    return round(annual_revenue_loss, 2)


def calculate_roi_score(annual_savings):
    """
    Simple ROI scoring logic (for demo impact).
    """
    if annual_savings > 2000000:
        return 9.5
    elif annual_savings > 1000000:
        return 8.5
    elif annual_savings > 500000:
        return 7.5
    else:
        return 6.5
