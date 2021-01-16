
function sendFriendRequest(id, csrfToken, updateUI){
    let payload = {
        'reciever_user_id': id
    }
    // const URL = {% url 'friends:send-friend-req' %}
    const URL = "/friends/send-friend-request/"
    console.log(JSON.stringify(payload))
    // const CSRF_TOKEN = "{{ csrf_token }}"
    const HEADERS = {
        "Content-type": "application/json, charset=UTF-8", 
        "X-CSRFToken": csrfToken, 
        'X-Requested-With': 'XMLHttpRequest'
    }

    fetch(URL, {
        method: 'POST',
        credentials: 'same-origin',
        headers: HEADERS,
        body: JSON.stringify(payload),
    })
    .then(response => response.json())
    .then(json => { console.log(json)
                    if(json['result'] == "success"){
                        alert(json['response'])
                        updateUI()
                    } else if(json['result'] == "error"){
                        alert(json['response'])
                    }
                }
        )
    // .catch(err => console.log(err))
}