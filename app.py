import falcon
from falcon_cors import CORS
from falcon_multipart.middleware import MultipartMiddleware
import user


# https://github.com/lwcolton/falcon-cors
# https://github.com/yohanboniface/falcon-multipart
cors = CORS(allow_all_origins=True,
            allow_credentials_all_origins=True,
            allow_all_headers=True,
            allow_all_methods=True)
api = falcon.API(middleware=[cors.middleware, MultipartMiddleware()])

api.add_route('/users',
              user.UserCollection())
api.add_route('/users/{id_}',
              user.UserItem())
api.add_route('/users/login',
              user.UserLogin())
api.add_route('/users/logout',
              user.UserLogout())
api.add_route('/users/resetpassword',
              user.ResetPassword())
api.add_route('/users/changepassword',
              user.ChangePassword())
api.add_route('/privileges',
              user.PrivilegeCollection())
api.add_route('/privileges/{id_}',
              user.PrivilegeItem())

# from waitress import serve
# serve(api, host='0.0.0.0', port=8886)
