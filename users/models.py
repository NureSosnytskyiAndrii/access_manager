from django.db import models
from django.contrib.auth.models import AbstractUser
import hashlib
import json
from datetime import datetime


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    permissions = models.JSONField(default=dict)

    def __str__(self):
        return self.name


class BlockchainBlock(models.Model):
    index = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()
    previous_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64)
    proof = models.PositiveIntegerField(default=0)

    @staticmethod
    def calculate_hash(index, timestamp, proof, data, previous_hash):
        block_string = f"{index}{timestamp}{proof}{json.dumps(data, sort_keys=True)}{previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = self.calculate_hash(
                self.index,
                self.timestamp,
                self.proof,
                self.data,
                self.previous_hash,
            )
        super().save(*args, **kwargs)

    @classmethod
    def create_genesis_block(cls):
        if cls.objects.exists():
            return cls.objects.first()
        genesis_block = cls.objects.create(
            index=1,
            timestamp=datetime.now(),
            data={},
            previous_hash="0",
            proof=100,
        )
        return genesis_block

    @classmethod
    def get_last_block(cls):
        return cls.objects.order_by("-index").first()

    @staticmethod
    def proof_of_work(previous_proof):
        """
       Proof of work for adding new block
        """
        new_proof = 1
        check_proof = False
        while not check_proof:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()
            ).hexdigest()
            if hash_operation[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    @classmethod
    def add_block(cls, data):
        """
        Add a new block to blockchain with proof of work
        """
        last_block = cls.get_last_block()
        new_index = last_block.index + 1
        new_proof = cls.proof_of_work(last_block.proof)
        new_block = cls.objects.create(
            index=new_index,
            timestamp=datetime.now(),
            data=data,
            previous_hash=last_block.hash,
            proof=new_proof,
        )
        return new_block

    @classmethod
    def is_chain_valid(cls):
        blocks = cls.objects.order_by("index")
        for i in range(1, len(blocks)):
            current_block = blocks[i]
            previous_block = blocks[i - 1]

            if current_block.previous_hash != previous_block.hash:
                return False

            hash_operation = hashlib.sha256(
                str(current_block.proof**2 - previous_block.proof**2).encode()
            ).hexdigest()
            if not hash_operation.startswith("0000"):
                return False
        return True


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    access_level = models.IntegerField(default=0)

    def __str__(self):
        return self.username

    def has_permission(self, permission):
        if self.role and permission in self.role.permissions:
            return True
        return False
