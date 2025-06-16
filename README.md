# Dustkid Leaderboard

This project is a web application that pulls leaderboard information from the Dustkid API for a game. It presents the data in a structured format, allowing users to track progress on custom content.

## Project Structure

```
dustkid-leaderboard
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── dustkid_api.py
│   ├── templates
│   │   └── leaderboard.html
│   └── static
│       └── style.css
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd dustkid-leaderboard
   ```

2. **Install Dependencies**
   Make sure you have Python installed. Then, install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   Start the application by running the main script:
   ```bash
   python app/main.py
   ```

4. **Access the Leaderboard**
   Open your web browser and navigate to `http://localhost:8000` to view the leaderboard.

## Usage

- The application fetches leaderboard data from the Dustkid API based on predefined level IDs.
- Users can view the leaderboard for different areas of the game, including 100% and any% completion times and scores.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.