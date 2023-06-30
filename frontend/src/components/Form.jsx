import React, {useContext, useState} from 'react';
import ErrorMessage from "./ErrorMessage";
import Button from "./GetButton"
import './App.css'
const Form = () => {
    const [vkdomain, setVkdomain] = useState("");
    const [postAmount, setPostAmount] = useState("");
 const [showLoader, setShowLoader] = useState(false)

    const [errorMessage, setErrorMessage] = useState("");

    const getPosts = async () => {
        setShowLoader(true);
        const requestOptions = {
            method: "GET",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                // "Accept": "application/json",
            },
        };
        var amountToFetch = 0

        if (postAmount == 0) {
            console.log("Я в условии на 0")
            amountToFetch = 500
        } else if (postAmount > 1000) {
            console.log("Я в условии на больше 1000")
            amountToFetch = 1000
        } else {
            amountToFetch = postAmount
        }

        const params = {
            domain: vkdomain,
            amount: amountToFetch,
        }
        console.log(amountToFetch)
        const response = await fetch("/api/v1/posts" + "?" + new URLSearchParams(params), requestOptions);
        const data = await response.json();

        if (!response.ok) {
            setErrorMessage(data.detail);
        } else {
            console.log(data)
            // setToken(data.access_token);
        }
setShowLoader(false);
    };

    const handleGetPosts = (e) => {
        e.preventDefault();
        getPosts();
    }

    return (
        <div className="column">
            <form className="box" onSubmit={handleGetPosts}>
                <div className="field">
                    <label className="label">Адрес человека или сообщества</label>
                    <div className="control">
                        <input
                            type="text"
                            placeholder="Например: vk.com/durov, vk.com/anime, durov, anime"
                            value={vkdomain}
                            onChange={(e) => setVkdomain(e.target.value)}
                            className="input"
                            required
                        />
                    </div>
                </div>
                <div className="field">
                    <label className="label">Количество (10-1000)</label>
                    <div className="control">
                        <input
                            type="number"
                            defaultValue={100}
                            onChange={(e) => setPostAmount(e.target.value)}
                            className="input"
                            required
                            min={0}
                            max={1000}
                            inputMode="numeric"
                            pattern="\d*"
                        />
                    </div>
                </div>

                <ErrorMessage message={errorMessage}/>
                <br/>
                <Button
      text="Получить посты"
      loading={showLoader}
      disabled={showLoader}
    />

            </form>
        </div>
    );

}

export default Form;
