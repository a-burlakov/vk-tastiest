import React, {useContext, useState} from 'react';
import ErrorMessage from "./ErrorMessage";
import Button from "./GetButton"
import '../assets/App.css'
import {defaultFormatUtc} from "moment";

const Form = () => {
    const [vkdomain, setVkdomain] = useState("");
    const [postAmount, setPostAmount] = useState("");
    const [showLoader, setShowLoader] = useState(false)
    const [postsData, setPostsData] = useState([])
    const [errorMessage, setErrorMessage] = useState("");

    const getPosts = async () => {
        setShowLoader(true);
        const requestOptions = {
            method: "GET",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
        };
        var amountToFetch = 0

        if (postAmount == 0) {
            amountToFetch = 100
        } else if (postAmount > 1000) {
            amountToFetch = 1000
        } else {
            amountToFetch = postAmount
        }

        const params = {
            domain: vkdomain,
            amount: amountToFetch,
        }

        const response = await fetch("/api/v1/posts" + "?" + new URLSearchParams(params), requestOptions);
        const data = await response.json();

        if (!response.ok) {
            setErrorMessage(data.detail);
        } else {
            setPostsData(data);
        }

        setShowLoader(false);
    };

    const handleGetPosts = (e) => {
        e.preventDefault();
        getPosts();
    }

    return (

        <div className="container">
            <div className="container">
                <div className="columns is-fullwidth is-centered">
                    <div className="column is-half">
                        <form className="box " onSubmit={handleGetPosts}>
                            <div className="field">
                                <label className="label">Адрес человека или
                                    сообщества</label>
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
                                <label className="label">Количество постов для показа (10-1000)</label>
                                <div className="control">
                                    <input
                                        type="number"
                                        defaultValue={100}
                                        onChange={(e) => setPostAmount(e.target.value)}
                                        className="input"
                                        required
                                        min={1}
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
                </div>
            </div>
            <br/>

            {postsData.length > 0 ? (
                <div className="container ">
                    {postsData.map((post) => (
                        <div key={post.id}>


                            <div className="box mb-5 is-half">
                                <div className="author">
                                    <div className="go">
                                        <a href={"https://vk.com/"+post.path}
                                           target="_blank"
                                           className="btn btn-default"><i
                                            className="fa fa-vk"></i> открыть пост →</a>
                                    </div>

                                </div>
                                <div className="text">
                                    {post.text}
                                </div>

                                <br/>
                                {/*{Date.prototype.fromisoformat(post.date)}*/}
                                {/*{post.date}*/}
                                {/*<div clas sName="attachments">*/}
                                    {post.photos.map((photo) => (
                                        <div key={photo.url}>
                                            <a href={"https://vk.com/"+post.path} target="_blank">
                                                <img className="mb-1" src={photo.url}/>
                                            </a>
                                        </div>
                                    ))}
                                {/*</div>*/}

                                <br/>
                                <div className="counters">
                                    <span className="likes"><i
                                        className="fa fa-heart-o"></i> {post.likes}</span>
                                </div>
                            </div>


                        </div>
                    ))}
                </div>

            ) : (<div></div>)}

        </div>


    )
        ;

}

export default Form;
