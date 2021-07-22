function sendFriendRequest(URL, ID, csrfToken, updateUI) {
  let payload = {
    receiver_user_id: ID,
  };

  console.log(JSON.stringify(payload));

  const HEADERS = {
    "Content-type": "application/json, charset=UTF-8",
    "X-CSRFToken": csrfToken,
    "X-Requested-With": "XMLHttpRequest",
  };
  console.log(payload);

  fetch(URL, {
    method: "POST",
    credentials: "same-origin",
    headers: HEADERS,
    body: JSON.stringify(payload),
  })
    .then((response) => response.json())
    .then((json) => {
      console.log(json);
      if (json["result"] == "success") {
        //alert(json['response'])
        updateUI();
      } else if (json["result"] == "error") {
        alert(json["response"]);
      }
    });
}

function acceptFriendRequest(URL, ID, updateUI) {
  const HEADERS = {
    "Content-type": "application/json, charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
  };
  URL = URL + "?friend_req_id=" + ID;
  fetch(URL, {
    method: "GET",
    headers: HEADERS,
  })
    .then((response) => response.json())
    .then((json) => {
      console.log(json);
      if (json["result"] == "success") {
        //alert(json['response'])
        updateUI();
      } else if (json["result"] == "error") {
        alert(json["response"]);
      }
    });
}

function declineFriendRequest(URL, ID, updateUI) {
  const HEADERS = {
    "Content-type": "application/json, charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
  };
  URL = URL + "?friend_req_id=" + ID;
  fetch(URL, {
    method: "GET",
    headers: HEADERS,
  })
    .then((response) => response.json())
    .then((json) => {
      console.log(json);
      if (json["result"] == "success") {
        //alert(json['response'])
        updateUI();
      } else if (json["result"] == "error") {
        alert(json["response"]);
      }
    });
}

function removeFriend(URL, ID, updateUI) {
  const HEADERS = {
    "Content-type": "application/json, charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
  };
  URL = URL + "?removee_id=" + ID;
  fetch(URL, {
    method: "GET",
    headers: HEADERS,
  })
    .then((response) => response.json())
    .then((json) => {
      console.log(json);
      if (json["result"] == "success") {
        //alert(json['response'])
        updateUI();
      } else if (json["result"] == "error") {
        alert(json["response"]);
      }
    });
}

function cancelFriendRequest(URL, ID, updateUI) {
  const HEADERS = {
    "Content-type": "application/json, charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
  };
  URL = URL + "?receiver_id=" + ID;
  fetch(URL, {
    method: "GET",
    headers: HEADERS,
  })
    .then((response) => response.json())
    .then((json) => {
      console.log(json);
      if (json["result"] == "success") {
        //alert(json['response'])
        updateUI();
      } else if (json["result"] == "error") {
        alert(json["response"]);
      }
    });
}
