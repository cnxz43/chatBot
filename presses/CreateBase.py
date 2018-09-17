# -*- coding:utf-8 -*-


from py2neo import Graph,Node,Relationship


def delete_all(graph, node, rel):
    graph.delete(rel)
    graph.delete(node)
    # graph.delete_all()

def find_node(graph, label, key, value):
    '''
    查找节点
    :param graph:
    :param label:
    :param key:
    :param value:
    :return:
    '''
    find_code_1 = graph.find_one(
        label="Person",
        property_key="name",
        property_value="test_node_1"
    )
    # print(find_code_1['name'])


# def create_a_node(graph, label, name, id):
#     node = Node(label=label, name=name)
#     # print("###",node)
#     graph.create(node)
#     return node


#创建关系
def create_relation(graph, node1, node2):
    '''
    建立node1和node2之前的双向边
    :param graph:
    :param node1:
    :param node2:
    :return:
    '''
    # print(type(node1),type(node2))
    node_1_call_node_2 = Relationship(node1, 'REL', node2)
    node_1_call_node_2['count'] = 1
    node_2_call_node_1 = Relationship(node2, 'REL', node1)
    node_2_call_node_1['count'] = 2
    graph.create(node_1_call_node_2)
    graph.create(node_2_call_node_1)


def connect_graph(username="neo4j", password="root"):

    graph = Graph(
        "http://localhost:7474",
        username=username,
        password=password
    )
    return graph

# import sys
if __name__=="__main__":
    print ('start connect...')
    # try:
    #     ip_address = sys.argv[1]
    # except:
    #     ip_address = "localhost"

    SA_graph = connect_graph()
    SA_graph.delete_all()

    houduan = ['分布式服务', '服务端组件', '分布式数据访问', '基础组件', '基础控件', '页面引擎', '横切关注']
    fenbushi_server = ['远程调用', '协议集成', '集群监控', '动态部署', '服务治理']
    fuwuduanzujian = ['分布式文件系统', '分布式缓存系统', '分布式计算']



    sta_node = Node("start", name="后端架构师")
    SA_graph.create(sta_node)

    for name in houduan:
        new_node = Node("levelone", name=name)
        SA_graph.create(new_node)
        create_relation(SA_graph, sta_node, new_node)

    node1 = SA_graph.find_one(
        label="levelone",
        property_key="name",
        property_value="分布式服务"
    )

    for name in fenbushi_server:
        new_node = Node("fenbushi_server", name=name)
        SA_graph.create(new_node)
        create_relation(SA_graph,node1, new_node)


    node2 = SA_graph.find_one(
        label="levelone",
        property_key="name",
        property_value="服务端组件"
    )
    for node in fuwuduanzujian:
        new_node = Node("fuwuduanzujian", name=name)
        SA_graph.create(new_node)
        create_relation(SA_graph, node2, new_node)