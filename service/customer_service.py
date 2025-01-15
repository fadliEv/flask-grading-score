from entity.customer import CustomerResponse

class CustomerService:
    @staticmethod
    def get_customer() -> CustomerResponse:
        # Contoh data customer statis
        return CustomerResponse(id=1, name="John Doe", email="john.doe@example.com")
