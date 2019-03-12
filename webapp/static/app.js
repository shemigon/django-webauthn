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
    signupSuccess: function () {
      console.log('User signed up successfully');
    },
    errorCallback: function (err) {
      console.error(err);
    },
    userNotFoundCallback: function (msg) {
      console.warn(msg);
    },
    userExistsCallback: function (msg) {
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
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body),
      });
    },
    FormRequest: function (route, form) {
      return new Request(route, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new FormData(form),
      });
    },
    getUsername: function (sel) {
      const userElems = document.querySelectorAll(sel);
      if (userElems.length > 1) {
        console.warn(
          `Found ${userElems.length} username inputs for "${sel}". Will use the first one.`,
        );
      } else if (!userElems.length) {
        throw `Username input cannot be found by "${sel}" selector.`;
      }
      const value = userElems[0].value;
      if (typeof value === 'undefined') {
        throw `Cannot user ${userElems[0].tagName} as username field.`;
      }
      return userElems[0].value.trim();
    },
    handleError: function (err) {
      // console.error(err);
      const params = window.webauthn.params;
      try {
        err = JSON.parse(err);
      } catch (e) {
      }

      if (err.username) {
        err.username.forEach(function (item) {
          switch (item.code) {
            case 100:
              if (params.userNotFoundCallback) {
                params.userNotFoundCallback(item.message);
              }
              break;
            case 101:
              if (params.userExistsCallback) {
                params.userExistsCallback(item.message);
              }
              break;
            default:
              params.errorCallback(`Unknown error: ${item.message}`)
          }
        });
      } else {
        console.log(err);
      }
    },
  },

  addLoginHandler: function ({usernameInputSel, buttonSel}) {
    document.addEventListener('DOMContentLoaded', function () {
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
        return params.handleError('Username cannot be blank.');
      }
      fetch(utils.JSONRequest(params.urlCredentialsGet, {username}))
        .then(function (res) {
          return res.json();
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
              params.handleError('Error in navigator.credentials.get: ' + err);
            });
        })
        .catch(params.handleError);
    }
  },

  addSignupHandler: function ({usernameInputSel, buttonSel}) {
    document.addEventListener('DOMContentLoaded', function () {
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
          el.addEventListener('click', signup);
        });
      } else {
        const form = usernameElem.closest('form');
        if (!form) {
          throw `Username field ${usernameInputSel} does not have an enclosing form.`;
        }
        form.addEventListener('submit', function (e) {
          e.preventDefault();
          signup();
        });
      }
    });

    const params = this.params;
    const utils = this.utils;

    function signup() {
      // See https://www.w3.org/TR/webauthn/#registering-a-new-credential
      const username = utils.getUsername(usernameInputSel);
      if (!username) {
        return params.handleError('Username cannot be blank.');
      }
      fetch(utils.JSONRequest(params.urlCredentialsCreate, {'username': username}))
        .then(function (res) {
          return res.json();
        })
        .then(function (options) {
          if (options.errors) {
            utils.handleError(options.errors);
            return;
          }
          options.challenge = utils.base64ToArrayBuffer(options.challenge);
          options.user.id = new TextEncoder().encode(options.user.name);
          navigator.credentials.create({publicKey: options})
            .then(function (newCredentialInfo) {
              // Send new credential info to server for verification and registration
              const dataForServer = {
                attestation_object: utils.arrayBufferToBase64(newCredentialInfo.response.attestationObject),
                client_data_json: utils.arrayBufferToBase64(newCredentialInfo.response.clientDataJSON),
              };
              dataForServer.username = btoa(username);
              fetch(utils.JSONRequest(params.urlCredentialsRegister, dataForServer))
                .then(function (res) {
                  debugger;
                  return res.blob();
                })
                .then(function (body) {
                  const reader = new FileReader();
                  reader.onload = function () {
                    params.signupSuccess(reader.result);
                  };
                  reader.readAsText(body);
                });
            })
            .catch(function (err) {
              params.handleError('Error in navigator.credentials.create: ' + err);
            });
        })
        .catch(params.handleError);
    }

  },

};
