
import { ReactComponent as Loader } from "./loader.svg"
const Button = ({ text, loading, disabled }) => {
  return (
    <button className="button is-primary is-fullwidth" type="submit" disabled={disabled}>
      {!loading ? text : <Loader className="spinner" />}
    </button>
  )
}

export default Button