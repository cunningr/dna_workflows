FROM python:3.8.3-slim-buster
RUN pip3 install dna_workflows==0.0.21
# RUN dna_workflows --install-url https://wwwin-github.cisco.com/_codeload/cxea/dnawf_dnac_module_pack/zip/@@BRANCH@@
WORKDIR /home/exec
CMD ["/bin/bash"]