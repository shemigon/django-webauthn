window.WebAuthnApp = function ({credentialsCreate, credentialsRegister, credentialsGet, verify}) {
  let urls = {
    credentialsCreate: credentialsCreate,
    credentialsRegister: credentialsRegister,
    credentialsGet: credentialsGet,
    verify: verify,
  };

  function message(msg, clear = true, style) {
    let el = document.getElementById("result");
    if (clear) {
      el.innerHTML = msg;
    } else {
      el.innerHTML += "\n" + msg;
    }
    el.className = style || "";
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

  this.createCredentials = function () {
    // See https://www.w3.org/TR/webauthn/#registering-a-new-credential
    const email = document.webauthn_input.email.value;
    let that = this;
    if (!email.trim()) {
      return error('Email cannot be blank!');
    }
    fetch(JSONRequest(urls.credentialsCreate, {email}))
      .then(function (res) {
        return res.json()
      }).then(function (options) {
      options.challenge = base64ToArrayBuffer(options.challenge);
      options.user.id = new TextEncoder().encode(options.user.name);
      console.log("Credential create options:");
      console.dir(options);
      navigator.credentials.create({publicKey: options}).then(function (newCredentialInfo) {
        console.log("Created credential:");
        console.dir(newCredentialInfo);
        // Send new credential info to server for verification and registration
        const dataForServer = {};
        ["attestationObject", "clientDataJSON"].map(f => {
          dataForServer[f] = arrayBufferToBase64(newCredentialInfo.response[f]);
        });
        dataForServer.email = btoa(email);
        fetch(JSONRequest(urls.credentialsRegister, dataForServer)).then(function (res) {
          console.log("Response from registerCredential:");
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
        console.log("Error in navigator.credentials.create: " + err);
        console.dir(err); // No acceptable authenticator or user refused consent
      });
    });
  };

  this.login = function () {
    // See https://www.w3.org/TR/webauthn/#verifying-assertion
    const email = document.webauthn_input.email.value;
    let that = this;
    if (!email.trim()) {
      return error('Email cannot be blank!');
    }
    fetch(JSONRequest(urls.credentialsGet, {email}))
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
        const dataForServer = {};
        ["authenticatorData", "clientDataJSON", "signature", "userHandle", "rawId"].map(f => {
          dataForServer[f] = arrayBufferToBase64(assertion.response[f]);
        });
        dataForServer.email = btoa(email);
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
