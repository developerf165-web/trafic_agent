"""
Dashboard Simulation Script
Replicates the logic of GeneralStats3.vue locally by calling the production API.
"""
import requests
import json
from datetime import datetime, timedelta
import sys

# Configuration
API_BASE_URL = "http://89.23.101.59:8001/api"
LOGIN_USER = "admin@example.com" # Default or provided by user
LOGIN_PASS = "admin_password" # Default or provided by user

class DashboardSimulator:
    def __init__(self, username=None, password=None):
        self.session = requests.Session()
        self.username = username or "admin@example.com"
        self.password = password or "9721" # Using the password found in .env
        self.token = None

    def login(self):
        """Authenticate with the backend"""
        print(f"🔑 Воҳидшавӣ ба сервер (Logging in to {API_BASE_URL})...")
        try:
            # The backend uses OAuth2PasswordRequestForm which expects x-www-form-urlencoded
            response = self.session.post(
                f"{API_BASE_URL}/auth/login",
                data={"username": self.username, "password": self.password}
            )
            response.raise_for_status()
            self.token = response.json()["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print("✅ Пайвастшавӣ муваффақ! (Login successful)\n")
            return True
        except Exception as e:
            print(f"❌ Хатои воҳидшавӣ (Login failed): {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response: {e.response.text}")
            return False

    def get_clients(self):
        """Fetch list of projects"""
        try:
            response = self.session.get(f"{API_BASE_URL}/clients/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching clients: {e}")
            return []

    def get_stats(self, client_id=None, days=14):
        """Fetch summary and dynamics"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "platform": "all"
        }
        if client_id:
            params["client_id"] = client_id

        print(f"📊 Гирифтани маълумот барои давраи: {start_date} то {end_date}...")
        
        try:
            # 1. Summary
            summary_res = self.session.get(f"{API_BASE_URL}/dashboard/summary", params=params)
            summary_res.raise_for_status()
            summary = summary_res.json()

            # 2. Dynamics (Chart data)
            dynamics_res = self.session.get(f"{API_BASE_URL}/dashboard/dynamics", params=params)
            dynamics_res.raise_for_status()
            dynamics = dynamics_res.json()

            return summary, dynamics
        except Exception as e:
            print(f"❌ Error fetching stats: {e}")
            return None, None

    def display_dashboard(self, summary, dynamics, client_name="Ҳамаи проектҳо"):
        """Print data in terminal"""
        print("\n" + "="*60)
        print(f"ДАШБОРД: {client_name}")
        print("="*60)
        
        # Summary Table
        print(f"{'Нишондиҳанда (KPI)':<25} | {'Қимат (Value)':<15}")
        print("-" * 45)
        print(f"{'Расход (Expenses)':<25} | {summary.get('expenses', 0):>10.2f} ₽")
        print(f"{'Показы (Impressions)':<25} | {summary.get('impressions', 0):>10}")
        print(f"{'Клики (Clicks)':<25} | {summary.get('clicks', 0):>10}")
        print(f"{'Лиды (Leads)':<25} | {summary.get('leads', 0):>10}")
        print(f"{'Цена клика (CPC)':<25} | {summary.get('cpc', 0):>10.2f} ₽")
        print(f"{'Цена лида (CPA)':<25} | {summary.get('cpa', 0):>10.2f} ₽")
        print("="*60)

        # Last 5 days dynamics
        if dynamics and dynamics.get('labels'):
            print("\nДинамикаи охирин (Recent Dynamics):")
            print(f"{'Сана (Date)':<12} | {'Харҷ (Cost)':>10} | {'Лид (Leads)':>5}")
            print("-" * 35)
            labels = dynamics['labels'][-5:]
            costs = dynamics['costs'][-5:]
            leads = dynamics['leads'][-5:]
            for i in range(len(labels)):
                print(f"{labels[i]:<12} | {costs[i]:>10.2f} | {leads[i]:>5}")
            print("-" * 35)

def main():
    # Attempt to use credentials from .env if available locally, else ask or use defaults
    simulator = DashboardSimulator()
    
    if not simulator.login():
        user = input("Логин (email): ")
        pw = input("Парол: ")
        simulator = DashboardSimulator(user, pw)
        if not simulator.login():
            sys.exit(1)

    clients = simulator.get_clients()
    
    print("Проектҳои дастрас (Available Projects):")
    print(f"0. Ҳамаи проектҳо (All Projects)")
    for i, c in enumerate(clients, 1):
        print(f"{i}. {c['name']}")
    
    choice = input("\nПроектро интихоб кунед (рақам): ")
    try:
        idx = int(choice)
        selected_client_id = None
        selected_name = "Ҳамаи проектҳо"
        
        if idx > 0 and idx <= len(clients):
            selected_client_id = clients[idx-1]['id']
            selected_name = clients[idx-1]['name']
            
        summary, dynamics = simulator.get_stats(selected_client_id)
        if summary:
            simulator.display_dashboard(summary, dynamics, selected_name)
            
    except ValueError:
        print("Интихоби нодуруст.")

if __name__ == "__main__":
    main()
