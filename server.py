from flask import Flask
from flask import request
from flask import render_template

from datetime import datetime
import numpy as np
import tensorflow_hub as hub
import tensorflow as tf
import json


app = Flask(__name__, static_folder="static")


module_url = "./96e8f1d3d4d90ce86b2db128249eb8143a91db73"


# Create graph and finalize (optional but recommended).
g = tf.Graph()
with g.as_default():
    text_input = tf.placeholder(dtype=tf.string, shape=[None])
    embed = hub.Module(module_url)
    my_result = embed(text_input)
    init_op = tf.group(
        [tf.global_variables_initializer(), tf.tables_initializer()])
g.finalize()

# Create session and initialize.
session = tf.Session(graph=g)
session.run(init_op)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


@app.route("/", methods=['GET'])
def land():
    return render_template('index.html')


@app.route("/similar", methods=['GET', 'POST'])
def similar():
    print(request.data)
    data = json.loads(request.data)
    print(data)
    print([data["a"], data["b"]])

    my_result_out = session.run(
        my_result, feed_dict={text_input: [data["a"], data["b"]]})
    # print(my_result_out)
    corr = np.inner(my_result_out, my_result_out)

    # , cls=NumpyEncoder)
    return json.dumps({"value": float(corr[0][1])}, cls=NumpyEncoder)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
