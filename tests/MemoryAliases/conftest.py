import pytest

from cfpq_data.config import RELEASE_INFO

mas = RELEASE_INFO['MemoryAliases']


@pytest.fixture(scope='session', params=[
    name
    for name, _ in mas.items()
])
def ma_graph_name(request):
    return request.param
