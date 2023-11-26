import time
import threading
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware


# 链名称到链ID的映射函数
def get_chain_id(blockchain_name):
    chain_ids = {
        "ETH": 1,  # 以太坊
        "BNB": 56,  # 币安链
        "MATIC": 137,  # Polygon (Matic)
        "AVAX": 43114,  # Avalanche
        "ARB": 42161,  # Arbitrum
        "BASE": 8453,  # 示例
        "OP": 10,  # Optimism
        # 添加更多链
    }
    return chain_ids.get(blockchain_name, None)


# 连接到区块链的函数
def connect_to_chain(api_url, blockchain_name, inject_poa_middleware=False):
    w3 = Web3(HTTPProvider(api_url))
    chain_id = get_chain_id(blockchain_name)
    if chain_id is None:
        raise ValueError("未知的区块链名称")
    if inject_poa_middleware:
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3, chain_id


# 定义mint函数，用于创建和发送交易
def mint(wallet_index, i, w3, from_address, private_key, nonce, json_data, chain_id, additional_fee, total_num):
    encoded_data = w3.to_hex(text=json_data)
    transaction = {
        'to': from_address,
        'value': w3.to_wei(0, 'ether'),
        'nonce': nonce,
        'chainId': chain_id,
        'data': encoded_data,
        'type': 0x2,  # EIP-1559交易类型
    }
    estimated_gas = w3.eth.estimate_gas(transaction)
    gas_fee = w3.eth.fee_history(1, 'latest', reward_percentiles=[50])
    recommended_priority_fee = gas_fee['reward'][0][0]
    max_priority_fee_per_gas = recommended_priority_fee + additional_fee
    base_fee = w3.eth.get_block('latest')['baseFeePerGas']
    max_fee_per_gas = base_fee + max_priority_fee_per_gas
    transaction['gas'] = estimated_gas
    transaction['maxPriorityFeePerGas'] = max_priority_fee_per_gas
    transaction['maxFeePerGas'] = max_fee_per_gas
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    timesline = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    progress = (i + 1) / total_num * 100  # 计算并显示进度
    print(f"{timesline} 钱包序号:{wallet_index}   当前mint: {i + 1}/{total_num}   进度: {progress:.2f}%   交易哈希: {txn_hash.hex()}")

    return nonce + 1


# 多线程执行函数
def worker(wallet_index, wallet, api_url, blockchain_name, json_data, num, additional_fee):
    try:
        w3, chain_id = connect_to_chain(api_url, blockchain_name)
        assert w3.is_connected()
        w3.eth.get_block('latest')
    except:
        # print(f"钱包 {wallet_index} - 连接到链时出错，尝试注入POA中间件: {e}")
        w3, chain_id = connect_to_chain(api_url, blockchain_name, inject_poa_middleware=True)
        assert w3.is_connected()

    nonce = w3.eth.get_transaction_count(wallet['address'])
    for i in range(num):
        try:
            # 调整参数以匹配 mint 函数的定义
            nonce = mint(wallet_index,i, w3, wallet['address'], wallet['private_key'], nonce, json_data, chain_id, additional_fee, num)
        except Exception as e:
            print(f'钱包 {wallet_index} - 当前错误轮次：{i + 1}  {e}')
            nonce = w3.eth.get_transaction_count(wallet['address'])
            time.sleep(5)


# 创建多线程的函数
def create_threads(wallets, api_urls, blockchain_name, json_data, num, additional_fee):
    threads = []
    for index, (wallet, api_url) in enumerate(zip(wallets, api_urls)):
        thread = threading.Thread(target=worker, args=(index + 1, wallet, api_url, blockchain_name, json_data, num, additional_fee))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


# 主函数
if __name__ == '__main__':
    #多个钱包就写多个钱包私钥和RPC节点，一一对应的，尽量多2个RPC，防止一家太卡mint太慢

    wallets = [{'address': '钱包1','private_key': '私钥1'},{'address': '钱包2','private_key': '私钥2'}]  # 钱包信息
    api_urls = ['RPC1','RPC2']  # RPC节点信息
    blockchain_name = 'MATIC'  # 区块链名称，注意大写(参考第8行)
    json_data = 'data:,{"a":"NextInscription","p":"oprc-20","op":"mint","tick":"NI","amt":"10000"}'  # 交易数据
    num = 1000  # 交易次数
    additional_fee = Web3.to_wei(10, 'gwei')  # 额外加速的Gas费用

    create_threads(wallets, api_urls, blockchain_name, json_data, num, additional_fee)
