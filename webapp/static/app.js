window.initWebAuthnHandlers = function (
  {
    credentialsCreate, credentialsRegister, credentialsGet, verify,
    usernameInputSel, signupSel, loginSel
  }
) {
  const urls = {
    credentialsCreate: credentialsCreate,
    credentialsRegister: credentialsRegister,
    credentialsGet: credentialsGet,
    verify: verify,
  };

  document.addEventListener("DOMContentLoaded", function () {
    Object.entries({
      [signupSel]: createCredentials,
      [loginSel]: login
    }).forEach(function ([sel, fn]) {
      const elems = document.querySelectorAll(sel);
      if (!elems.length) {
        throw `No elements found by "${sel}"`;
      }
      elems.forEach(function (el) {
        el.addEventListener('click', fn);
      });
    });
  });

  function message(msg = '', clear = true, style = '') {
    let el = document.getElementById("result");
    if (clear) {
      el.innerHTML = msg;
    } else {
      el.innerHTML += "\n" + msg;
    }
    el.className = style;
  }

  function error(msg) {
    message(msg, true, 'error');
  }

  function arrayBufferToBase64(a) {
    return btoa(String.fromCharCode(...new Uint8Array(a)));
  }

  function base64ToArrayBuffer(b) {
    return Uint8Array.from(atob(b), c => c.charCodeAt(0));
  }

  function JSONRequest(route, body) {
    return new Request(route, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(body)
    });
  }

  function getUsername() {
    const userElems = document.querySelectorAll(usernameInputSel);
    if (userElems.length > 1) {
      console.warn(
        `Found ${userElems.length} username inputs for "${usernameInputSel}". Will use the first one.`
      );
    } else if (!userElems.length) {
      throw `No elements found by "${usernameInputSel}."`
    }
    return userElems[0].value.trim();
  }

  function createCredentials() {
    // See https://www.w3.org/TR/webauthn/#registering-a-new-credential
    message();
    const username = getUsername();
    if (!username) {
      return error('Username cannot be blank.');
    }
    fetch(JSONRequest(urls.credentialsCreate, {username: username}))
      .then(function (res) {
        return res.json()
      })
      .then(function (options) {
        if (options.errors) {
          return error(options.errors);
        }
        options.challenge = base64ToArrayBuffer(options.challenge);
        options.user.id = new TextEncoder().encode(options.user.name);
        console.log("Credential create options:");
        console.dir(options);
        navigator.credentials.create({publicKey: options})
          .then(function (newCredentialInfo) {
            console.log("Created credential:");
            console.dir(newCredentialInfo);
            // Send new credential info to server for verification and registration
            const dataForServer = {
              attestation_object: arrayBufferToBase64(newCredentialInfo.response.attestationObject),
              client_data_json: arrayBufferToBase64(newCredentialInfo.response.clientDataJSON),
            };
            dataForServer.username = btoa(username);
            fetch(JSONRequest(urls.credentialsRegister, dataForServer))
              .then(function (res) {
                console.log("Response from credentialsRegister:");
                console.dir(res);
                return res.blob();
              })
              .then(function (body) {
                const reader = new FileReader();
                reader.onload = function () {
                  message(reader.result);
                };
                reader.readAsText(body);
              });
          }).catch(function (err) {
          console.log("Error in navigator.credentials.create: " + err);
          console.dir(err); // No acceptable authenticator or user refused consent
        });
      });
  }

  function login() {
    // See https://www.w3.org/TR/webauthn/#verifying-assertion
    message();
    const username = getUsername();
    if (!username) {
      return error('Username cannot be blank.');
    }
    fetch(JSONRequest(urls.credentialsGet, {username}))
      .then(function (res) {
        return res.json()
      }).then(function (options) {
      options.challenge = base64ToArrayBuffer(options.challenge);
      for (let cred of options.allowCredentials) {
        cred.id = Uint8Array.from(atob(cred.id), c => c.charCodeAt(0));
      }
      console.log("Credential get options:");
      console.dir(options);
      navigator.credentials.get({publicKey: options}).then(function (assertion) {
        // Send assertion to server for verification
        console.log("Got assertion:");
        console.dir(assertion);
        const dataForServer = {
          username: btoa(username),
          authenticator_data: arrayBufferToBase64(assertion.response.authenticatorData),
          client_data_json: arrayBufferToBase64(assertion.response.clientDataJSON),
          signature: arrayBufferToBase64(assertion.response.signature),
          user_handle: arrayBufferToBase64(assertion.response.userHandle),
          raw_id: arrayBufferToBase64(assertion.response.rawId),
        };
        fetch(JSONRequest(urls.verify, dataForServer)).then(function (res) {
          console.log("Response from verifyAssertion:");
          console.dir(res);
          return res.blob();
        }).then(function (body) {
          const reader = new FileReader();
          reader.onload = function () {
            message(reader.result);
          };
          reader.readAsText(body);
        });
      }).catch(function (err) {
        console.log("Error in navigator.credentials.get: " + err);
        console.dir(err); // No acceptable credential or user refused consent
      });
    });
  }
};
