from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User, Role, BlockchainBlock
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user and add a block to blockchain
    """
    username = request.data.get("username")
    password = request.data.get("password")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    email = request.data.get("email")
    role_id = request.data.get("role_id")
    access_level = request.data.get("access_level")

    try:
        role = Role.objects.get(id=role_id)
    except Role.DoesNotExist:
        return Response({"error": "Role does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=role,
        access_level=access_level,
    )

    block_data = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "role": role.name,
        "access_level": access_level,
    }
    BlockchainBlock.add_block(block_data)

    return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_user(request):
    """
    Auth user login and return
    """
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if user is not None:

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "message": "Login successful",
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "access_level": user.access_level,
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def chain_valid(request):
    """
    Validate the blockchain integrity.
    """
    is_valid = BlockchainBlock.is_chain_valid()
    if is_valid:
        return Response({"message": "Blockchain is valid"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Blockchain is invalid"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_chain(request):
    """
    Retrieve the entire blockchain.
    """
    blocks = BlockchainBlock.objects.order_by("index")
    chain = []
    for block in blocks:
        chain.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "data": block.data,
            "hash": block.hash,
            "previous_hash": block.previous_hash,
            "proof": block.proof,
        })

    return Response({
        "length": len(chain),
        "chain": chain,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """
    Get all users
    """
    if not request.user.role or request.user.role.name != "admin":
        return Response({"error": "Only administrators can view users"}, status=status.HTTP_403_FORBIDDEN)

    users = User.objects.all().values(
        "id", "username", "email", "first_name", "last_name", "access_level", "role__name"
    )
    return Response({"users": list(users)}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_access_level(request):
    if not request.user.role or request.user.role.name != "admin":
        return Response({"error": "Only administrators can update access levels"}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get("user_id")
    new_access_level = request.data.get("access_level")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

    user.access_level = new_access_level
    user.save()

    return Response({"message": "Access level updated successfully"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_role(request):

    if not request.user.role or request.user.role.name != "admin":
        return Response({"error": "Only administrators can update user roles"}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get("user_id")
    new_role_id = request.data.get("role_id")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

    try:
        role = Role.objects.get(id=new_role_id)
    except Role.DoesNotExist:
        return Response({"error": "Role does not exist"}, status=status.HTTP_404_NOT_FOUND)

    user.role = role
    user.save()

    return Response({"message": "User role updated successfully"}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):

    if not request.user.role or request.user.role.name != "admin":
        return Response({"error": "Only administrators can delete users."}, status=status.HTTP_403_FORBIDDEN)

    try:
        user_to_delete = User.objects.get(id=user_id)

        if user_to_delete.id == request.user.id:
            return Response({"error": "You cannot delete yourself."}, status=status.HTTP_400_BAD_REQUEST)

        user_to_delete.delete()
        return Response({"message": f"User with ID {user_id} deleted successfully."}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"error": f"User with ID {user_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)