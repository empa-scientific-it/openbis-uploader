from platform import python_branch
import pybis

ob = pybis.Openbis("https://localhost:8443", verify_certificates=False, token=None, use_cache=False)

#This should fail
try:
    token = ob.login('wrong','wrong', False)
except ValueError:
    print(ob.token)
    print("Wrong login")