from logging_config import logger
def transform_data(data: dict):
    """
    Convert all fields into human-friendly format
    
    :param data: JSON data
    :type data: dict
    """
    # Convert all to be have order of magnitude instead of raw numbers
    if data.get("net_loss"):
        data["net_income"]["value"] = data["net_loss"]
    if data.get("operating_loss"):
        data["operating_income"]["value"] = data["operating_loss"]

    to_be_converted = [("total_revenue", "value"), ("net_income", "value"), ("operating_income", "value"), 
                       ("operating_expenses", "value"), ("buybacks_and_dividends", "buybacks"), ("buybacks_and_dividends", "dividends"), ("buybacks_and_dividends", "combined")]
    for metric, key in to_be_converted:
        value = data[metric][key]
        if metric != "buybacks_and_dividends":
            if value:
                data[metric] = magnitude(value)
        else:
            if value:
                data[metric][key] = magnitude(value)
    # Adjust 
    if data["earnings_per_share"]["value"]:
        eps = data["earnings_per_share"]["value"]
        data["earnings_per_share"] = f"${str(eps)}"
    if data["gross_margin"]["value"]:
        gross = data["gross_margin"]["value"]
        data["gross_margin"] = f"{str(gross)}%"

    for metric in data.keys():
        if metric != "buybacks_and_dividends" and isinstance(data[metric], dict):
            if data[metric].get("yoy") or data[metric].get("qoq"):
                percent_string = ""
                yoy = data[metric]["yoy"]
                qoq = data[metric]["qoq"]
                if yoy:
                    percent_string += f"{yoy}% YoY"
                if qoq:
                    if yoy:
                        percent_string += f", {qoq}% QoQ"
                    else:
                        percent_string += f"{qoq}% QoQ"
                data[metric] = percent_string
            else:
                data[metric] = None
    

    # Combine buybacks and dividends
    bb, div, combined = data["buybacks_and_dividends"]["buybacks"], data["buybacks_and_dividends"]["dividends"], data["buybacks_and_dividends"]["combined"]
    bb_div_string = ""
    if not bb and not div and combined:
        bb_div_string = f"{str(combined)} Buybacks and Dividends"
    else: 
        if bb:
            bb_div_string += f"{str(bb)} Buybacks"
        if div:
            if bb:
                bb_div_string += f", {str(div)} Dividends"
            else:
                bb_div_string += f"{str(div)} Dividends"
    
    data["buybacks_and_dividends"] = bb_div_string

    # Delete all middleman keys
    del data["net_loss"]
    del data["operating_loss"]
    logger.info(data)

def valid_table(table):
    """
    Check to make sure the table isn't mostly empty
    
    :param table: table
    """
    total_cells = 0
    dead_cells = 0
    for row in table:
        dead_cells += row.count(None) + row.count("")
        total_cells += len(row)
    return dead_cells/total_cells < 0.5

def magnitude(number: float):
    """
    Converts a number to Decimal + order of magnitude format (i.e. 1.3B)
    
    :param number: number to be adjusted
    :type number: float
    """
    map_list = [(1e9, "B"), (1e6, "M"), (1e3, "K")]
    for value, letter in map_list:
        if abs(number) > value:
            divided = f"{number/value:.2f}".rstrip('0').rstrip('.')
            return f"${divided}{letter}"
    return number