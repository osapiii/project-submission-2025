export const useNotes = () => {
  const notes = {
    fileTemplateRegisterModalNote: {
      title: "ファイルテンプレート登録",
      description:
        "ファイルテンプレートを登録する画面です。PPTX/PDF/txt/html/mdファイルに対応しています。",
    },
    datasourceRegisterInput: {
      title: "データソース登録",
      description:
        "データソースを登録する画面です。データソースの種類によって、接続情報の入力方法が異なります。",
    },
    datasourceRegisterTestConnect: {
      title: "テスト抽出",
      description:
        "設定情報を元にデータソースにテスト抽出します。接続に成功し、出力データに問題ない場合は、データソース登録実行ボタンを押してください。",
    },
    materialMaster: {
      title: "原料マスタ",
      description:
        "製品に使用される原料の一覧です。タイプ別に複数種類登録することで、A:通常営業日用 / B:定休日用などと使い分けることができます。原価や、1日あたりの生産量が生産計画作成時にインプットとして使用されます。",
    },
    productMaster: {
      title: "製品マスタ",
      description:
        "製品の一覧です。登録した情報を元に出荷分析や、生産シミュレーションが実行されます。",
    },
    simulationParameter: {
      title: "生産ルール",
      description:
        "生産ルールは、生産計画作成時にインプットとして使用される情報です。日付によって異なるルールを使用することもできます。",
    },
    simulationParameterScoreWeight: {
      title: "日別のスコアの重み付け",
      description:
        "d21=21日先の欠品の重み付け、d90=90日先の欠品の重みと言った具合に、将来日付の欠品の重み付けを設定します。先回り生産のタイミングで本重み付けは使用され、欠品補充のタイミングでは使用されません。",
    },
    calendarMapping: {
      title: "稼働カレンダー",
      description:
        "ある日付に使用される【原料マスタ】/【製品マスタ】/【生産ルール】の組み合わせを設定します。こちらの登録内容に従って、生産計画作成が実行されます。",
    },
    shippingEventAnalysis: {
      title: "出荷分析画面",
      description:
        "登録されている出荷予定をインプットに、分析やAIチャットを実行できる画面です。",
    },
    shippingEventAnalysisCustomTag: {
      title: "カスタムタグ",
      description:
        "出荷予定にカスタムタグを付与することで、出荷予定をグルーピングして分析することができます。タグは最大10個まで登録可能で、使用するタグは切り替えボタンでアクティブにすると画面や分析内容に反映されます。",
    },
    masterSet: {
      title: "マスタ登録画面",
      description:
        "各種マスタを登録する為の画面です。画面上で直接入力する物と、マスタの更新ボタンから進んでCSV・Googleシート連携可能なものがあります。生産計画・販売分析・原料管理の全てが本マスタに基づいて実行されるので、業務で実際に使用している正確なデータを登録することを心がけてください。",
    },
    simulatorInputConfig: {
      title: "シミュレーションの動作設定",
      description:
        "生産計画を生成する日数 と 計算の起点となる日付を入力します。",
    },
    simulatorInputCurrentStock: {
      title: "現在在庫の登録",
      description:
        "生産計画シミュレーターは、【本日時点での在庫数】+ 【今後の出荷予定】の2つを元に生成されます。最新の現在在庫数を登録するようにしてください。",
    },
    simulatorInputCalendar: {
      title: "現在在庫の変動予定",
      description:
        "カレンダー形式で、仮に一切生産を行わなかった場合の在庫変動を確認できます。特に💣マークは、出荷数 > 当日在庫のいわゆる出荷不良にあたり、生産計画では💣マークを与えられた条件を守りながら最小限にする事をゴールに動作します。",
    },
  };

  return ref(notes);
};
