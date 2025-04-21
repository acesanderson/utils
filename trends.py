import pandas as pd
from pytrends.request import TrendReq
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import time
import random
import sys

# --- Configuration ---
CHART_HEIGHT = 15  # Height of the chart in characters
CHART_WIDTH = 75  # Width of the chart in characters
TIMEFRAME = "today 12-m"  # Timeframe for trends (last 12 months)
GEO = "US"  # Geographic region (e.g., 'US', '' for Global)
COLORS = ["[bold blue]", "[bold red]", "[bold green]"]  # Colors for terms 1, 2, 3
CHARS = ["█", "*", "+"]  # Characters for terms 1, 2, 3
MAX_RETRIES = 3  # Max retries for fetching data
RETRY_DELAY = 5  # Seconds to wait between retries

# --- Initialize Rich Console ---
console = Console()

# --- Functions ---


def get_trends_data(keywords):
    """
    Fetches Google Trends 'Interest Over Time' data.

    Args:
        keywords (list): A list of 1 to 3 keyword strings.

    Returns:
        tuple: (pandas.DataFrame containing interest over time, list of keywords with data)
               Returns (None, original_keywords) if an error occurs or no data found.
    """
    if not 1 <= len(keywords) <= 3:
        console.print("[bold red]Error: Please provide 1 to 3 keywords.[/]")
        return None, keywords  # Return None for df, original keywords

    original_keywords = list(keywords)  # Keep a copy
    # Use the original_keywords list for pytrends payload initially
    current_keywords_for_payload = list(original_keywords)

    pytrends = TrendReq(hl="en-US", tz=360)  # tz=360 is US Central Time offset from UTC

    for attempt in range(MAX_RETRIES):
        try:
            # Use original_keywords for printing the attempt message
            console.print(
                f"Attempting to fetch data for: {', '.join(original_keywords)} (Attempt {attempt + 1}/{MAX_RETRIES})..."
            )
            # Use the potentially modified list for the payload
            pytrends.build_payload(
                current_keywords_for_payload,
                cat=0,
                timeframe=TIMEFRAME,
                geo=GEO,
                gprop="",
            )
            df = pytrends.interest_over_time()

            if df.empty:
                console.print(
                    "[yellow]Warning: No data returned for the given keywords/timeframe.[/]"
                )
                return None, original_keywords

            # Drop the 'isPartial' column if it exists
            if "isPartial" in df.columns:
                df.drop(columns=["isPartial"], inplace=True)

            # Check if all keyword columns requested in this attempt are present
            missing_keywords = [
                kw for kw in current_keywords_for_payload if kw not in df.columns
            ]
            if missing_keywords:
                console.print(
                    f"[yellow]Warning: No data found for keyword(s): {', '.join(missing_keywords)}. They will be excluded.[/]"
                )
                # Update keywords list to only those with data for the next potential retry or final return
                current_keywords_for_payload = [
                    kw for kw in current_keywords_for_payload if kw in df.columns
                ]
                if (
                    not current_keywords_for_payload
                ):  # All keywords failed in this attempt
                    return (
                        None,
                        original_keywords,
                    )  # Return original list as no data was found for any
                # Return the dataframe subset and the list of keywords that actually have data
                console.print("[green]Partial data fetched successfully![/]")
                return df[current_keywords_for_payload], current_keywords_for_payload

            console.print("[green]Data fetched successfully![/]")
            # Return the full dataframe (subset if partial) and the list of keywords with data
            return df[current_keywords_for_payload], current_keywords_for_payload

        except Exception as e:
            console.print(f"[bold red]Error fetching data: {e}[/]")
            # Check specifically for 429 error code
            is_rate_limit_error = False
            # Check based on exception type or message content
            if (
                isinstance(e, ConnectionError) and "response code 429" in str(e).lower()
            ):  # Example check
                is_rate_limit_error = True
            elif "429" in str(e):  # General check in error string
                is_rate_limit_error = True

            if is_rate_limit_error:
                console.print(
                    f"[yellow]Rate limit likely hit. Waiting {RETRY_DELAY} seconds before retrying...[/]"
                )
                time.sleep(RETRY_DELAY + random.uniform(0, 2))  # Add jitter
            elif attempt < MAX_RETRIES - 1:
                console.print(
                    f"[yellow]Waiting {RETRY_DELAY} seconds before retrying...[/]"
                )
                time.sleep(RETRY_DELAY)
            else:
                console.print("[bold red]Max retries reached. Failed to fetch data.[/]")
                return None, original_keywords  # Return original list on final failure
    # Return None and the original keywords list if loop finishes unexpectedly
    return None, original_keywords


def create_ascii_chart(df, keywords):
    """
    Creates a simple ASCII chart string and a separate legend object.

    Args:
        df (pandas.DataFrame): The DataFrame containing trends data.
        keywords (list): The list of keywords corresponding to columns in df.

    Returns:
        tuple: (str containing the formatted ASCII chart, rich.text.Text legend object)
               Returns (None, None) if chart cannot be generated.
    """
    if df is None or df.empty:
        console.print("[red]Cannot generate chart: No data available.[/]")
        return None, None

    num_points = len(df.index)
    if num_points == 0:
        console.print("[red]Cannot generate chart: No data points.[/]")
        return None, None

    # Create the chart grid (list of lists or list of strings)
    # Initialize with spaces
    grid = [[" " for _ in range(CHART_WIDTH)] for _ in range(CHART_HEIGHT)]

    # Plot data points
    for i in range(num_points):
        # Calculate x position (time axis)
        # Ensure division by zero doesn't happen if num_points is 1
        x = min(int((i / max(1, num_points - 1)) * (CHART_WIDTH - 1)), CHART_WIDTH - 1)

        # Use the actual keywords list passed to this function
        for k_idx, keyword in enumerate(keywords):
            # Double-check keyword exists in DataFrame columns for safety
            if keyword not in df.columns:
                continue

            value = df.iloc[i][keyword]
            if pd.isna(value):
                continue  # Skip missing values for a point

            # Calculate y position (value axis) - 0 is bottom, CHART_HEIGHT-1 is top
            y = min(int((value / 100.0) * (CHART_HEIGHT - 1)), CHART_HEIGHT - 1)

            # Place character on grid (higher index = higher value)
            # Overwrite if multiple points land on the same spot (simplest approach)
            # Ensure k_idx is within bounds of COLORS and CHARS
            if k_idx < len(COLORS) and k_idx < len(CHARS):
                # Use the Rich markup tags directly here when building the grid string
                grid[y][x] = f"{COLORS[k_idx]}{CHARS[k_idx]}[/]"
            else:
                # Fallback if more keywords than defined colors/chars (shouldn't happen with input validation)
                grid[y][x] = "?"

    # --- Assemble the chart string with axes ---
    output_lines = []

    # Title - Use the keywords actually plotted
    title = f"Google Trends Interest: {', '.join(keywords)} ({TIMEFRAME}, {GEO if GEO else 'Global'})"
    output_lines.append(
        title.center(CHART_WIDTH + 4)
    )  # Center based on chart width + axis space
    output_lines.append("-" * (CHART_WIDTH + 4))

    # Y-Axis labels and Chart Area
    for y in range(CHART_HEIGHT - 1, -1, -1):  # Print from top to bottom
        # Calculate approximate value for the row label
        y_label_val = (
            int(round((y / max(1, CHART_HEIGHT - 1)) * 100))
            if CHART_HEIGHT > 1
            else (100 if y == 0 else 0)
        )
        # Add labels at top, bottom, and roughly halfway
        show_label_y = (y == CHART_HEIGHT - 1) or (y == 0) or (y == CHART_HEIGHT // 2)
        y_label = f"{y_label_val:3d}|" if show_label_y else "   |"
        # Join the grid row which now contains Rich markup
        row_content = "".join(grid[y])
        output_lines.append(y_label + row_content)

    # X-Axis Line
    output_lines.append("---+" + "-" * CHART_WIDTH)

    # X-Axis Labels (Start and End Dates)
    start_date = df.index.min().strftime("%Y-%m-%d")
    end_date = df.index.max().strftime("%Y-%m-%d")
    # Ensure labels don't overlap
    label_space = CHART_WIDTH - len(start_date) - len(end_date)
    if label_space < 1:
        label_space = 1  # Minimum 1 space
    x_axis_label_line = "   |" + start_date + " " * label_space + end_date
    output_lines.append(x_axis_label_line)

    # --- Create the Legend Object using Text.assemble ---
    legend_parts = [("Legend: ", "bold")]  # Start with ("text", "style") tuple
    # Use the actual keywords list passed to this function
    for k_idx, keyword in enumerate(keywords):
        # Ensure k_idx is within bounds of COLORS and CHARS
        if k_idx < len(COLORS) and k_idx < len(CHARS):
            # Extract style name from markup tag (e.g., "bold blue" from "[bold blue]")
            # Handle potential errors if format changes
            try:
                style_name = COLORS[k_idx].strip("[]")
            except:
                style_name = "default"  # Fallback style

            legend_parts.append(
                (CHARS[k_idx], style_name)
            )  # Add ("char", "style_name")
            legend_parts.append(
                (f" = {keyword}  ", "default")
            )  # Add ("text", "default_style")
        else:
            legend_parts.append((f"? = {keyword}  ", "default"))  # Fallback

    legend = Text.assemble(*legend_parts)

    # Return the joined chart string and the assembled legend Text object
    return "\n".join(output_lines), legend


# --- Main Execution ---
def main():
    """Gets user input, fetches data, and displays the chart."""
    console.print("[bold cyan]Google Trends ASCII Chart Generator[/]")
    console.print("Enter 1 to 3 search terms, separated by commas.")

    input_keywords = []
    while True:
        try:
            raw_input = input("Keywords: ")
            # Store the exact keywords entered by the user
            input_keywords = [kw.strip() for kw in raw_input.split(",") if kw.strip()]
            if 1 <= len(input_keywords) <= 3:
                break
            else:
                console.print(
                    "[yellow]Please enter between 1 and 3 non-empty keywords.[/]"
                )
        except EOFError:
            console.print("\n[bold red]Input aborted. Exiting.[/]")
            sys.exit(1)
        except KeyboardInterrupt:
            console.print("\n[bold red]Script interrupted by user. Exiting.[/]")
            sys.exit(1)

    # Fetch data - Pass the user's input keywords
    # get_trends_data now returns df and the list of keywords that actually have data
    trends_df, keywords_with_data = get_trends_data(input_keywords)

    # Create and display chart if data is available
    if trends_df is not None and not trends_df.empty and keywords_with_data:
        # Pass the dataframe and the list of keywords that have data to the chart function
        chart_str, legend_obj = create_ascii_chart(trends_df, keywords_with_data)

        if chart_str and legend_obj:
            # Use Panel for better framing using the chart string.
            # The chart string itself contains Rich markup for the plotted points.
            panel = Panel(
                chart_str,
                title="Trend Visualization",
                border_style="dim blue",
                padding=(1, 2),
            )
            console.print(panel)
            # Print the legend object separately using console.print, which handles Text objects correctly.
            console.print(legend_obj)
        else:
            console.print("[bold red]Failed to generate chart components.[/]")

    else:
        console.print(
            "[bold red]Could not generate chart due to data fetching issues or no data found.[/]"
        )


if __name__ == "__main__":
    main()
