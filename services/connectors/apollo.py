#!/usr/bin/env python3
"""Apollo.io connector for PayReady AI."""

import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime


class ApolloConnector:
    """Apollo.io API connector."""

    def __init__(self):
        self.api_key = os.getenv("APOLLO_IO_API_KEY")
        self.base_url = "https://api.apollo.io/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request to Apollo."""
        url = f"{self.base_url}/{endpoint}"

        if params is None:
            params = {}
        params["api_key"] = self.api_key

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=json_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def search_people(self,
                      organization_name: Optional[str] = None,
                      person_titles: Optional[List[str]] = None,
                      keywords: Optional[str] = None,
                      limit: int = 10) -> Dict[str, Any]:
        """Search for people in Apollo database."""
        data = {
            "page": 1,
            "per_page": limit
        }

        if organization_name:
            data["organization_name"] = organization_name

        if person_titles:
            data["person_titles"] = person_titles

        if keywords:
            data["q_keywords"] = keywords

        return self._make_request("POST", "mixed_people/search", json_data=data)

    def get_account(self, account_id: str) -> Dict[str, Any]:
        """Get account details by ID."""
        return self._make_request("GET", f"accounts/{account_id}")

    def search_accounts(self,
                       name: Optional[str] = None,
                       domain: Optional[str] = None,
                       industry: Optional[str] = None,
                       limit: int = 10) -> Dict[str, Any]:
        """Search for accounts in Apollo database."""
        data = {
            "page": 1,
            "per_page": limit
        }

        if name:
            data["name"] = name

        if domain:
            data["domain"] = domain

        if industry:
            data["industry"] = industry

        return self._make_request("POST", "mixed_accounts/search", json_data=data)

    def get_person(self, person_id: str) -> Dict[str, Any]:
        """Get person details by ID."""
        return self._make_request("GET", f"people/{person_id}")

    def enrich_person(self, email: Optional[str] = None,
                     first_name: Optional[str] = None,
                     last_name: Optional[str] = None,
                     organization_name: Optional[str] = None) -> Dict[str, Any]:
        """Enrich person data."""
        data = {}

        if email:
            data["email"] = email

        if first_name:
            data["first_name"] = first_name

        if last_name:
            data["last_name"] = last_name

        if organization_name:
            data["organization_name"] = organization_name

        return self._make_request("POST", "people/match", json_data=data)

    def get_health_score(self, account_id: str) -> Dict[str, Any]:
        """Get health score for an account (custom implementation)."""
        account = self.get_account(account_id)

        if "error" in account:
            return account

        score = 100
        factors = []

        if account.get("employees"):
            if account["employees"] < 10:
                score -= 20
                factors.append("Small company size")
            elif account["employees"] > 1000:
                score += 10
                factors.append("Large enterprise")

        if account.get("last_activity_date"):
            last_activity = datetime.fromisoformat(account["last_activity_date"])
            days_inactive = (datetime.now() - last_activity).days
            if days_inactive > 90:
                score -= 30
                factors.append(f"Inactive for {days_inactive} days")
            elif days_inactive < 7:
                score += 15
                factors.append("Recently active")

        if account.get("phone_numbers"):
            score += 5
            factors.append("Has contact information")

        return {
            "account_id": account_id,
            "health_score": max(0, min(100, score)),
            "factors": factors,
            "account_data": account,
            "timestamp": datetime.utcnow().isoformat()
        }


apollo = ApolloConnector()


def main():
    """Test Apollo connector."""
    print("Apollo.io Connector Test")

    result = apollo.search_people(
        organization_name="OpenAI",
        person_titles=["CEO", "CTO", "VP Engineering"],
        limit=5
    )
    print(f"People search result: {result}")

    result = apollo.search_accounts(
        industry="Technology",
        limit=5
    )
    print(f"Account search result: {result}")


if __name__ == "__main__":
    main()