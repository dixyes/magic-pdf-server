
ARG BASE_IMAGE=nvcr.io/nvidia/cuda:12.4.1-devel-ubuntu22.04

FROM ${BASE_IMAGE}

WORKDIR /magicpdf

COPY requirements.txt /magicpdf

# install python and torch
RUN --mount=type=cache,id=pip-ubuntu22.04,target=/root/.cache/pip,sharing=private \
    --mount=type=cache,id=apt-ubuntu22,target=/var/cache/apt,sharing=private \
    # setup mirrors
    sed -e "s/archive.ubuntu.com/mirrors.ustc.edu.cn/g" \
        -e "s/security.ubuntu.com/mirrors.ustc.edu.cn/g" -i /etc/apt/sources.list && \
    # install deps via apt
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
        python3-dev python3-pip python3-wheel python3-setuptools python3-venv \
    && \
    # setup mirror
    python3 -m pip config set global.index-url https://mirrors.bfsu.edu.cn/pypi/web/simple && \
    # setup venv
    python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip install wheel && \
    pip install -r requirements.txt
    # override torch?
    # python3 -m pip install torch torchvision torchaudio \
    #     --index-url https://download.pytorch.org/whl/cu121
    #     # --pre --index-url https://download.pytorch.org/whl/nightly/cu124

COPY . /magicpdf/

VOLUME "/models"

ENTRYPOINT [ "/bin/sh", "-c" ]

# CMD [ "python3 -m uvicorn server:app --host 0.0.0.0 --port 8000" ]
CMD [ "start.sh" ]

EXPOSE 8000
