travel_flows = []


def append_travel_flow(travel_flow: dict):
    travel_flows.append(travel_flow)


def get_travel_flows(members: list, travel_date: str, relationship: str, purpose: str) -> dict:
    sorted_travel_flows = sorted(travel_flows, key=lambda travel_flow: travel_flow["flow_order"])
    return {
        "data": {
            "relevant_info": {
                "members": members,
                "travel_date`": travel_date,
                "relationship": relationship,
                "purpose": purpose
            },
            "flows_info": sorted_travel_flows
        }
    }


def clear_travel_flows():
    travel_flows.clear()
