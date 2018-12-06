# -*- coding:utf-8 -*-


from py2neo import Graph,Node,Relationship,NodeMatcher
import csv
import os
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(project_dir)

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

# from pinyin import PinYin
import pinyin
def people_graph_init(file_dir, pp_graph):
    csv_reader = csv.reader(open(file_dir, encoding='utf-8'))
    apart_node = Node("apartment", name="网管中心")
    pp_graph.create(apart_node)

    for row in csv_reader:
        print(row)

        name_pinyin = pinyin.get(row[1], format="strip", delimiter="")
        # print(name_pinyin)
        new_node = Node("people",
                        id=row[0],
                        name=row[1],
                        ph = row[3],
                        addr = "石家庄市裕华区昆仑大街89号",
                        email = name_pinyin + "@he.chinamobile.com")
        pp_graph.create(new_node)

        # room_node = pp_graph.find_one(
        #     label="room",
        #     property_key="name",
        #     property_value=row[2])
        matcher = NodeMatcher(pp_graph)
        room_node = matcher.match("room", name=row[2]).first()
        # print(room_node)

        if room_node:
            # print(room_node["name"])
            pass
        else:
            room_node = Node("room",name=row[2])
            pp_graph.create(room_node)
            r = Relationship(room_node, "belong", apart_node)
            pp_graph.create(r)
            r = Relationship(apart_node, "have", room_node)
            pp_graph.create(r)

        r = Relationship(new_node, "belong", room_node)
        pp_graph.create(r)
        r = Relationship(room_node, "have", new_node)
        pp_graph.create(r)


# import sys
if __name__=="__main__":
    print ('start connect...')
    # try:
    #     ip_address = sys.argv[1]
    # except:
    #     ip_address = "localhost"

    # SA_graph = connect_graph()
    # SA_graph.delete_all()

    # houduan = ['分布式服务', '服务端组件', '分布式数据访问', '基础组件', '基础控件', '页面引擎', '横切关注']
    # fenbushi_server = ['远程调用', '协议集成', '集群监控', '动态部署', '服务治理']
    # fuwuduanzujian = ['分布式文件系统', '分布式缓存系统', '分布式计算']
    #
    #
    #
    # sta_node = Node("start", name="后端架构师")
    # SA_graph.create(sta_node)
    #
    # for name in houduan:
    #     new_node = Node("levelone", name=name)
    #     SA_graph.create(new_node)
    #     create_relation(SA_graph, sta_node, new_node)
    #
    # node1 = SA_graph.find_one(
    #     label="levelone",
    #     property_key="name",
    #     property_value="分布式服务"
    # )
    #
    # for name in fenbushi_server:
    #     new_node = Node("fenbushi_server", name=name)
    #     SA_graph.create(new_node)
    #     create_relation(SA_graph,node1, new_node)
    #
    #
    # node2 = SA_graph.find_one(
    #     label="levelone",
    #     property_key="name",
    #     property_value="服务端组件"
    # )
    # for node in fuwuduanzujian:
    #     new_node = Node("fuwuduanzujian", name=name)
    #     SA_graph.create(new_node)
    #     create_relation(SA_graph, node2, new_node)


    # create connection
    pp_graph = connect_graph()
    pp_graph.delete_all()
    filepath = project_dir + '/static/people.csv'
    people_graph_init(filepath, pp_graph)