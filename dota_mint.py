from substrateinterface import SubstrateInterface, Keypair
from substrateinterface.exceptions import SubstrateRequestException

def make_transaction(substrate, keypair, receiver_address, amount):
    # 构建 transfer 调用
    transfer_call = substrate.compose_call(
        call_module='Balances',
        call_function='transfer_keep_alive',
        call_params={
            'dest': receiver_address,
            'value': amount
        }
    )

    # 构建 remark 调用
    remark_call = substrate.compose_call(
        call_module='System',
        call_function='remark',
        call_params={
            'remark': '{"p":"dot-20","op":"mint","tick":"DOTA"}'  # 根据需要调整参数
        }
    )

    # 构建批量调用
    batch_call = substrate.compose_call(
        call_module='Utility',
        call_function='batch_all',
        call_params={
            'calls': [transfer_call, remark_call]
        }
    )

    # 签名批量交易
    extrinsic = substrate.create_signed_extrinsic(call=batch_call, keypair=keypair)

    # 发送交易
    try:
        receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
        print(f"交易成功，哈希值: {receipt.extrinsic_hash}")
    except SubstrateRequestException as e:
        print(f"交易失败: {e}")

def main(num_transactions, mnemonic, receiver_address, amount):
    # 连接到波卡节点
    substrate = SubstrateInterface(
        url="wss://rpc.polkadot.io",
        ss58_format=0,
        type_registry_preset='polkadot'
    )

    # 从助记词创建 Keypair 对象
    keypair = Keypair.create_from_mnemonic(mnemonic)

    for i in range(num_transactions):
        print('dot开始运行')
        make_transaction(substrate, keypair, receiver_address, amount)

if __name__ == '__main__':
    # 设置参数
    num_transactions = 10000
    mnemonic = ""  # 你的助记词
    receiver_address = ""  # 接收者的地址
    amount = 0  # 例如，转账 1 DOT（注意单位换算）

    main(num_transactions, mnemonic, receiver_address, amount)
