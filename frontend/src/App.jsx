import React, {useContext, useEffect, useState} from "react";

// import Register from "./components/Register";
import Form from "./components/Form";
import Header from "./components/Header";
// import Table from "./components/Table";
// import { UserContext } from "./context/UserContext";

const App = () => {


    return (
        <>
            <Header/>
            <div className="columns">
              <div className="column"></div>
              <div className="column m-5 is-one-third">
                {/*{!token ? (*/}
                  <div className="columns">
                    <Form />
                  </div>
              {/*  ) : (*/}
              {/*    <Table />*/}
              {/*  )}*/}
              </div>
              <div className="column"></div>
            </div>
        </>
    );
};

export default App;
