window.webauthn = {
  params: { // must be set before use, the template tag does it
    // signup
    urlCredentialsCreate: null,
    urlCredentialsRegister: null,
    // login
    urlCredentialsGet: null,
    urlVerify: null,

    loginSuccess: function () {
        console.log('User logged in successfully');
    },
    errorCallback: function (err) {
        console.error(err);
    },
    userNotFoundCallback: function (msg) {
        console.warn(msg);
    },
  },

  utils: {
    arrayBufferToBase64: function (a) {
      return btoa(String.fromCharCode(...new Uint8Array(a)));
    },

    base64ToArrayBuffer: function (b) {
      return Uint8Array.from(atob(b), c => c.charCodeAt(0));
    },

    JSONRequest: function (route, body) {
      return new Request(route, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body)
      });
    },
    FormRequest: function (route, form) {
      return new Request(route, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new FormData(form),
      });
    },
    getUsername: function (sel) {
      const userElems = document.querySelectorAll(sel);
      if (userElems.length > 1) {
        console.warn(
          `Found ${userElems.length} username inputs for "${sel}". Will use the first one.`
        );
      } else if (!userElems.length) {
        throw `Username input cannot be found by "${sel}" selector.`
      }
      return userElems[0].value.trim();
    },
    handleError: function (err) {
      // console.error(err);
      const params = window.webauthn.params;
      try {
        err = JSON.parse(err);
      } catch (e) {}

      if (err.username) {
        err.username.forEach(function (item) {
            if (item.code === 100) {
              if (params.userNotFoundCallback) {
                params.userNotFoundCallback(item.message);
              }
            }
        })
      }
    }
  },

  addLoginHandler: function ({usernameInputSel, buttonSel}) {
    document.addEventListener("DOMContentLoaded", function () {
      const usernameElem = document.querySelector(usernameInputSel);
      if (!usernameElem) {
        throw `Cannot find username field ${usernameElem}`;
      }
      if (buttonSel) {
        const elems = document.querySelectorAll(buttonSel);
        if (!elems.length) {
          throw `No elements found by "${buttonSel}"`;
        }
        elems.forEach(function (el) {
          el.addEventListener('click', login);
        });
      } else {
        const form = usernameElem.closest('form');
        if (!form) {
          throw `Username field ${usernameInputSel} does not have an enclosing form.`;
        }
        form.addEventListener('submit', function (e) {
          e.preventDefault();
          login();
        });
      }
    });

    const params = this.params;
    const utils = this.utils;

    function login() {
      // See https://www.w3.org/TR/webauthn/#verifying-assertion
      const username = utils.getUsername(usernameInputSel);
      if (!username) {
        return utils.error('Username cannot be blank.');
      }
      fetch(utils.JSONRequest(params.urlCredentialsGet, {username}))
        .then(function (res) {
          return res.json()
        })
        .then(function (options) {
          if (options.errors) {
            utils.handleError(options.errors);
            return;
          }
          options.challenge = utils.base64ToArrayBuffer(options.challenge);
          for (let cred of options.allowCredentials) {
            cred.id = Uint8Array.from(atob(cred.id), c => c.charCodeAt(0));
          }
          navigator.credentials.get({publicKey: options})
            .then(function (assertion) {
              // Send assertion to server for verification
              const dataForServer = {
                username: btoa(username),
                authenticator_data: utils.arrayBufferToBase64(assertion.response.authenticatorData),
                client_data_json: utils.arrayBufferToBase64(assertion.response.clientDataJSON),
                signature: utils.arrayBufferToBase64(assertion.response.signature),
                user_handle: utils.arrayBufferToBase64(assertion.response.userHandle),
                raw_id: utils.arrayBufferToBase64(assertion.response.rawId),
              };
              fetch(utils.JSONRequest(params.urlVerify, dataForServer))
                .then(function (res) {
                  return res.blob();
                })
                .then(function (body) {
                  const reader = new FileReader();
                  reader.onload = function () {
                    try {
                      if (JSON.parse(reader.result).verified === true) {
                        params.loginSuccess(reader.result);
                        return;
                      }
                    } catch (e) {
                    }
                    console.error('Expected: {"verified": true}, got: ' + reader.result);
                  };
                  reader.readAsText(body);
                });
            })
            .catch(function (err) {
              params.errorCallback("Error in navigator.credentials.get: " + err);
            });
        })
        .catch(params.errorCallback);
    }
  },

};
