from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .blockchain import (
    get_land_parcel,
    get_plots_by_owner,
    split_and_transfer_land,
    register_land,
    get_user_role,
)

# Basic page views
def home(request):
    return render(request, 'home.html')

def register_land(request):
    return render(request, 'register_land.html')

def transfer_land(request):
    return render(request, 'transfer_land.html')

def lease_land(request):
    return render(request, 'lease_land.html')

def view_details(request):
    return render(request, 'view_details.html')

def split_land(request):
    return render(request, 'split_land.html')

def search_page(request):
    return render(request, 'search.html')


# API views
def get_land(request, plot_id):
    try:
        land = get_land_parcel(plot_id)
        print("Fetched from blockchain:", land)  # Debug output

        # Ensure the response is a tuple/list with at least 15 elements
        if not land or len(land) < 15:
            return JsonResponse({"error": "Invalid data received from blockchain."}, status=500)

        if not land[9]:  # isRegistered
            return JsonResponse({"error": "Plot not registered"}, status=404)

        data = {
            "plotId": land[0],
            "ownerName": land[1],
            "district": land[2],
            "subcounty": land[3],
            "parish": land[4],
            "village": land[5],
            "plotSize": land[6],
            "nationalNIN": land[7],
            "owner": land[8],
            "isRegistered": land[9],
            "registrationDate": land[10],
            "currentTenant": land[11],
            "leaseStartTime": land[12],
            "leaseEndTime": land[13],
            "isLeased": land[14]
        }
        return JsonResponse(data)

    except Exception as e:
        print("Error in get_land:", e)  # Debug output
        return JsonResponse({"error": f"Blockchain error: {str(e)}"}, status=500)


def search_by_owner_name(request, owner_name):
    try:
        matches = get_plots_by_owner(owner_name)
        return JsonResponse({"matchingPlotIds": matches})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def split_and_transfer_view(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            tx_hash = split_and_transfer_land(
                original_plot_id=body['originalPlotId'],
                new_plot_id=body['newPlotId'],
                new_owner_name=body['newOwnerName'],
                new_nin=body['newNIN'],
                new_owner_address=body['newOwnerAddress'],
                split_plot_size=int(body['splitSize']),
                sender_private_key=body['senderPrivateKey']
            )
            return JsonResponse({"status": "success", "txHash": tx_hash})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"message": "Invalid request"}, status=400)


@csrf_exempt
def register_land_view(request):
    """
    This view handles land registration.
    Checks user role from blockchain and requires sending the private key (NOT ideal for production).
    """
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            sender_address = body.get("senderAddress")
            sender_private_key = body.get("senderPrivateKey")
            # Check role on blockchain
            role = get_user_role(sender_address)
            if role != "Landowner":
                return JsonResponse({"status": "error", "message": "Only Landowners can register land"}, status=403)

            # Call blockchain function to register land (which requires payment of 0.01 ETH)
            tx_hash = register_land(
                plot_id=body['plotId'],
                owner_name=body['ownerName'],
                district=body['district'],
                subcounty=body['subcounty'],
                parish=body['parish'],
                village=body['village'],
                plot_size=int(body['plotSize']),
                national_nin=body['nationalNIN'],
                sender_private_key=sender_private_key
            )
            return JsonResponse({"status": "success", "txHash": tx_hash})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"message": "Invalid request"}, status=400)
