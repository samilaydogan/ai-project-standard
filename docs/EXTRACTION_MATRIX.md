# Extraction matrix — Stage 1

Prepared before standard content creation, 2026-09-26. Source is the read-only local ai-operation-hub working tree, including its existing uncommitted state. This audit is provenance, never consumer policy or application truth.

A = GENERIC AS-IS; B = GENERIC AFTER PARAMETERIZATION; C = PROJECT-SPECIFIC TEMPLATE; D = BUSINESS ONLY. No complete source file qualified as A: even broadly reusable documents contain local constraints. Historical release notes were reviewed for evidence conventions only. Missing root UI/catalog/changelog equivalents were located under docs/governance or docs. No AGENTS.md or tracked agent configuration was found. No external roadmap or future-direction note was opened.

| Source | Class | Treatment | SHA-256 |
| --- | --- | --- | --- |
| `AGENT_WORKFLOW.md` | B | Extract process invariants; remove local tools, identifiers, roles, storage topology, brands and product gates. | `0d3cc1a96df57e805aa13ef57c83a11997690c3ae8c218a3af5a81d2d0c58a61` |
| `DEVELOPMENT_RULES.md` | B | Extract process invariants; remove local tools, identifiers, roles, storage topology, brands and product gates. | `bbeaa235c895ab31a7aca34ae5f9053a03ace1eb0fa898066999cbb60a8ae2ff` |
| `EXECUTION_PLAN.md` | C | Retain document ownership/structure only; replace all project facts with placeholders. | `d9225421491b3c9ca1d45a8a70ff3106eaf0a2e43b85123d5138e5be55b47ba3` |
| `HANDOFF.md` | C | Retain document ownership/structure only; replace all project facts with placeholders. | `f059b5fb8b8ec652cb6c476b21be126f1b67c73e97ef1d8f07144812b0e92f3b` |
| `PROJECT_STATE.md` | C | Retain document ownership/structure only; replace all project facts with placeholders. | `29f1d5b278ea82231c4d0f347dd24b33256ecc99395b5f09e6d0803852f5d1ac` |
| `README.md` | B | Extract test isolation, redaction, live versus mocked evidence and installation safety only. | `fa298d1d373414defcb941329b169b1171592360bb68e278e77f6babf4190f17` |
| `THIRD_PARTY_LICENSE_INVENTORY.md` | B | Extract process invariants; remove local tools, identifiers, roles, storage topology, brands and product gates. | `d5142aaa807ac0f0a65dd02e8b260a13879ecbcf7c17275eb180289e3d9c74b9` |
| `docs/ADMIN_GUIDE.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `ec0af53d403574a3af06e73f2b97dd31d1728ac7f65f5885483734947f1d1de4` |
| `docs/CAPABILITY_CATALOG.md` | C | Retain document ownership/structure only; replace all project facts with placeholders. | `e44ce071fff1d6f8438974441e56addf403ad6f37a937234647d6780021d2805` |
| `docs/ELOGO_PHASE_A.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `baf7ef89d9368aa58720cabac2eb50652dced1e468b6bd7052783779af8d1d01` |
| `docs/INSTALLATION.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `a110be271e7d62c53712734c8bcf5902c8387465b840a503af82ed36bbfd2143` |
| `docs/INTEGRATION_ROADMAP.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `08499e4483711dcbd362a32f80456d83e4282b6d50d1022b0a3525793d886c03` |
| `docs/KVKK_ROADMAP.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `1c76eea7e59706d9096c5cdbf311d84aceb38ac8f548bc90279514343a125e24` |
| `docs/MIGRATION_RECOVERY.md` | B | Extract process invariants; remove local tools, identifiers, roles, storage topology, brands and product gates. | `750c459713796f6000fbdcd8849ced56ea576921669542d97eb533bd44acb06b` |
| `docs/PRIVACY_OPERATIONS.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `af569ad59de4372462f28c40d52bd6e092542dbfa42275325a9f9e3a48533f43` |
| `docs/PRODUCT_PORTAL.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `b2f99b50beb93381d5da6ff9e06079f99686d07d79ab96c24c8c566dac9a8adb` |
| `docs/PRODUCT_TOUR.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `078dc87cbcc913bf3d329f0c1ae436384e00d410e753dc042d83aee1dadcbdb6` |
| `docs/PROVIDER_CONFORMANCE_P1.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `06b44e830d7f5200cfb0db90b78db874c35b14fbf876c8d257527234c1522f47` |
| `docs/RELEASE_0.1.16.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `684848c56eaddec2fc848c9b3f98a64ab3807c413d97e507a6640528cffd433f` |
| `docs/RELEASE_0.1.17.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `f4954841a84219ef69e2edeaa277f21ef9d004aab73b80ebe643cd44eb5de75c` |
| `docs/RELEASE_0.1.18.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `f37e956c53bb4965aff72d3c48f95e0671932151bfb06c2eed81afd620d5ff4b` |
| `docs/RELEASE_0.1.19.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `c74e893d9e1bfabf827b2ea780960b3ce934b416d42742987b6c7d51a0e74cfb` |
| `docs/RELEASE_0.1.20.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `40fb880ac73bc33f9b47d15896e785dafdd7107810da68c5f2855e0115125490` |
| `docs/RELEASE_0.1.21.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `b984675cee0acf51a24701ed03a9aba59403f5b47ddad0c0a1db3315d48830ba` |
| `docs/RELEASE_0.1.26.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `0040fc3d0f3d85fed1ca5d9abb0f8efde66bca414cde2c5d2179c13074365b54` |
| `docs/RELEASE_0.1.27.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `3fd45e5bc0fc679b0353791031ff66e1424b9c857666b74774cf4be2e612699f` |
| `docs/RELEASE_0.1.28.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `d2cf5fe8cc20724a87eb6b6c6933109ecb7d5a88a9d812bc366b730ff62299cc` |
| `docs/RELEASE_0.1.29.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `23dc3ec923285ebc01d8a3dfa1f1c842b8e40ccaa6b8b7d14714756c5465f4ec` |
| `docs/RELEASE_0.1.30.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `6067a2e7e57ae205fb18b93a9341b641bb37d028b98d151b27d1e849d15d9e92` |
| `docs/RELEASE_0.1.31.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `b90da89213db776374e30b8e448295c9cad43decee06a313c5cef42f2609062f` |
| `docs/RELEASE_0.1.32.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `7c5f7057519a7caf47b0f61bb3614dde2cbf61aa3e82d5988ece7b1c60b4c492` |
| `docs/RELEASE_0.10.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `cf9cdab35226b733b565c16e4d6973487879266b3d82ba37482b034e4be9caff` |
| `docs/RELEASE_0.11.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `edd984461fcc1c5f7dc4878b92fdc5189c2728c615016d193f777e8510705123` |
| `docs/RELEASE_0.12.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `e2064a10b03f4c94f6f39226d4f6d9a74177114eccd86bfd1ff281c6f66fdcd8` |
| `docs/RELEASE_0.13.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `ef72a8825573c2f1bc3fa8166422a827f61902d087010da160f92ef449e79daf` |
| `docs/RELEASE_0.14.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `08b030a052b0026dbefa383e4adfa3fd8ee005e49ce0dd1e62b9ce2e15204d61` |
| `docs/RELEASE_0.15.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `012f04d5c099ce6948ec3c6821425709ab72e74ace8c5d5567117df48ede8f02` |
| `docs/RELEASE_0.16.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `72bac1db579fb932b36693140f83c11d7f044ba4b6417cbfab1c76cc4315123d` |
| `docs/RELEASE_0.16.1.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `9d177123cce18e5cdda5becd27cc5e003fb7d1cc034745131d257b68de7ec7f1` |
| `docs/RELEASE_0.16.2.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `e779369f17d56975d822d8bff7ebcc64705dccfe47b0e60c2f4765e40f242ca0` |
| `docs/RELEASE_0.17.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `4bc009c6c27e8afb807e9ebf524387c766833a8f8104bf9d73fbcc86a47d333f` |
| `docs/RELEASE_0.18.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `05ce3b8b1eab6235decbcb41ec6df05fe466821f29f89e9f160aee8f291fe0fe` |
| `docs/RELEASE_0.19.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `3fb99a3a6620c1ee498ff4cff17257b5145c61e9e711d3d2e732d01822c4fc8b` |
| `docs/RELEASE_0.19.1.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `61c482f0621028f001c687f0bb67f9b0609d1c294ebbe1ef32b5c997e8b0072a` |
| `docs/RELEASE_0.19.2.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `acf7e8de1547b83708c5cfebd69efdbb6169d9f4ac5fa14470cf78e192d7e35c` |
| `docs/RELEASE_0.2.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `fce60d4871eba4dd115c62a25f2921c49edad62c835c8255a01ef2fc7ccaa63d` |
| `docs/RELEASE_0.2.1.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `d7143109296ca089c2b23e6c916f30385a3946f4030da96bab01388c169b2da3` |
| `docs/RELEASE_0.2.10.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `49069f3dd5f867f06ae5b2f5e73957484c1ce749955b91969286be0e96cdcdcb` |
| `docs/RELEASE_0.2.11.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `55730d7155ae591fcb53ce430acf5b466ba4bb85967251fbc10cd54805b75468` |
| `docs/RELEASE_0.2.12.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `7afce938f8e5d9ac27dc6f6f12ae6bb4f2d6418d281041f965e2e87076259951` |
| `docs/RELEASE_0.2.13.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `1cc5bb4505a2bdcfd4bc136ddaf49037888d78e49540060268aa09bd0da81e6a` |
| `docs/RELEASE_0.2.14.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `ea432ae46f24c3f6a4846cb2889a71e28bf147c49a12e8a7f7ce3af63d663790` |
| `docs/RELEASE_0.2.15.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `ba279c9f8f30898dd898786ee3dcba2cdb8238e689b95dfc40e2d7a13b34c28e` |
| `docs/RELEASE_0.2.16.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `7ab0caa15b42c4b672e00b43ac8a60524a6d507188d962e98079360e31c710c3` |
| `docs/RELEASE_0.2.17.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `71c5172f96dc6ffe344548d528d9e0f09d10bdfca38446fffe7a39ce8e772055` |
| `docs/RELEASE_0.2.18.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `aec18a9e3f919930e7c41eab7b833806f2e018e374a750f21d4f82b186e45359` |
| `docs/RELEASE_0.2.19.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `dcf1db0020af644880637df4d34b7de50e0369dbdc3314554db62bba81af583a` |
| `docs/RELEASE_0.2.2.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `63a9356e4bf9c7d5850564477d698bbdf05d7af084a9f7cf2c30714f0c30470c` |
| `docs/RELEASE_0.2.20.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `40c127b44207315a6a3bae54363db8237b18ac5971eec5d4333eb319d0192d14` |
| `docs/RELEASE_0.2.21.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `3ea2bdf425334e194e9b2d89abb4393cd1437ae328369d71a4464f4f6c30e67b` |
| `docs/RELEASE_0.2.22.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `4b01d8b253875633ae26c87a5730aa7d736d85fb20c9c235bac3013eadd47af9` |
| `docs/RELEASE_0.2.23.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `3c39fa125dfb0547ade6f0aa5985edc7e419a839515d7bff921a364276ecbeba` |
| `docs/RELEASE_0.2.24.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `e1ebd162665e30e05ef8581c142860067b6039b27ba4022640056f69ed4cf95c` |
| `docs/RELEASE_0.2.25.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `2e17f2314d6bc0b116a309c0c4e93ec98f75968c04c46bba3964b4e505198c5a` |
| `docs/RELEASE_0.2.26.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `cba7d0cae434f3ab101d4e36c621f0722bf66a82aa8602693dfb33f2a6b25912` |
| `docs/RELEASE_0.2.27.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `027e349f29275c793c62f0448faec7391ea5b7939206cbaebc6af4956b56a5c4` |
| `docs/RELEASE_0.2.28.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `a47dd55b399a1f11ac80ee14eacc57969845d8b8afe31d49be493a0a0dc0d7bf` |
| `docs/RELEASE_0.2.29.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `2ceae89bd0677560780ef5a0d8f42e0631301ff10242c13c42f4ebf6f58b24fb` |
| `docs/RELEASE_0.2.3.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `f7edcff09cb4ed3cf9f9535b114e2fc2df85459f771ae1db3e8c2df5c51a5766` |
| `docs/RELEASE_0.2.30.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `014aaf558ffa46327119b5b9521a0d1aac5bead2646f1ea48c3ea357003963e3` |
| `docs/RELEASE_0.2.31.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `33c173e7ef837700ad15f3855a5b1945569817efc2dbb1fc330da644198439ee` |
| `docs/RELEASE_0.2.32.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `5210e09b6ec5c95e3532bb234135e580ed76fc9ad5e205ca747d79ce44b2030a` |
| `docs/RELEASE_0.2.4.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `fafe98143ebcc2fc4dc97805bf3288ace55b3ce03e3cf7f4292c65dbf532f4b2` |
| `docs/RELEASE_0.2.5.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `df2dc98174b8e6254bcf8763b296ce58aab6328f5a9f763e85986dc0b67539c5` |
| `docs/RELEASE_0.2.6.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `9d2d1085f8ad4911bc1cf53deacc22d84fa5ccf9fe9e2df4d96edad2e2fd339e` |
| `docs/RELEASE_0.2.7.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `19880e3f7bb02b9bcc4fbce544535432dd551f45a8dc9bf0cb338cf5e603d295` |
| `docs/RELEASE_0.2.8.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `2b8004cec8ba03df4df5e59d2982de32cc3267ea80c03d97735c8f8d0c71f34c` |
| `docs/RELEASE_0.2.9.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `be7a168f9934730e7c799b0148a34ab47d00ae7abe4dbbe3845bb8c6fbfa3d9a` |
| `docs/RELEASE_0.3.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `d6771064a24055c51036564ea2dabfd59371349b3faa934c3286caa68ef0e904` |
| `docs/RELEASE_0.3.1.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `26267741670c748de1fd8ce83b80d6d08edb06a1487f1ffa0048eeb709f498ca` |
| `docs/RELEASE_0.3.10.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `5ad21c67fb93710231a3a165ec328ffd1be188a301253fc805cc6cabcfe5d5d0` |
| `docs/RELEASE_0.3.11.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `230c7d1b453dfa09342ef47b3ba42abe9b37181f0ca84b55135703fbb6bf9374` |
| `docs/RELEASE_0.3.12.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `d460124f4aa97f83d3ad880b958665b4f6245f0ac3ed24a983308711ee10119e` |
| `docs/RELEASE_0.3.13.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `24cf2ce4a1a751b294a01714e5730e26240ab50db48332874fcbe218f26840be` |
| `docs/RELEASE_0.3.14.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `e48e1c45866141137c01a706700411121d17b2dd257cbcafb740e96bd4f49598` |
| `docs/RELEASE_0.3.15.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `093894fbd66d771e9da594d506bfa438c09176696583055a0a9c2962e3fd3aa5` |
| `docs/RELEASE_0.3.16.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `36a7f8e23ad93110e17a10fdadd3d0c700c9e5f7782ed0a94938d5cd5d83e2e7` |
| `docs/RELEASE_0.3.17.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `9e7f9530b66cb0b3f75d7086e97ac48a50cd3ac1eef1a01d468e538d123e21a2` |
| `docs/RELEASE_0.3.18.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `57a1f010f6ac80f2685a45684161b9d80be78bc75c2708c052c74c6f5496a7fa` |
| `docs/RELEASE_0.3.19.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `c6d77402f0ef008587249f879bea1b9496c2d64d76a0a61e4c99c04c892e659c` |
| `docs/RELEASE_0.3.2.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `3f2462565aa16818fdbec41e1810de982724685aa7557b07264bb837241fb577` |
| `docs/RELEASE_0.3.20.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `a2b5a0d9b99d8b6bc3cefb10086038d0870fce14a1c20374a9f0bd4239d9240a` |
| `docs/RELEASE_0.3.21.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `1ab9186bd2335e340d50b905b84453a9d40d5eaee584d8b582d29bb2c75caced` |
| `docs/RELEASE_0.3.22.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `d2ea2d3051401c495478b4563cb77ccb0ec035c75842e0c1d11be5308f1e64e8` |
| `docs/RELEASE_0.3.23.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `7c8adfd079244d5c693b6490a6903510200be8c48710ce9b17c83aa01760c1e4` |
| `docs/RELEASE_0.3.24.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `9fda1788c50fbc64b22c78e1e5026457a973672416b26f39bb359f3bd729eb49` |
| `docs/RELEASE_0.3.25.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `0436e4dd960837bfbbce91fa5d8fdbc50718ac93de681ec282161087c2face92` |
| `docs/RELEASE_0.3.26.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `7936b4f3f6838cd0918ee9459c5867b65dfddc052862f0b6c042399b7c2df1bb` |
| `docs/RELEASE_0.3.27.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `ed32373c43b1c681b121de86d0783426664f0485e33d83dca697b9ff89802b44` |
| `docs/RELEASE_0.3.28.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `28e53b8df40a3ae58dc518d6428d013e1fa5d78ec8e19c4f64be0e180741d989` |
| `docs/RELEASE_0.3.29.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `43450b4b1b4e2fbd9ccfb977c537999f45799c7b10dccd6cf5b233d84d35d715` |
| `docs/RELEASE_0.3.3.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `93451c169e912263db7d25861e48d6ca2c743c888559748f61520ea8a9fe9cbd` |
| `docs/RELEASE_0.3.30.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `a25e45c0713e6ba0dc547c82e70137e41003b1765ab1f11d9f1f8aaccaf9b4bf` |
| `docs/RELEASE_0.3.31.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `be53ddc4d0c4fb3919227221cc4c0363dcecd8d43b361d57e2fc93b781cceb87` |
| `docs/RELEASE_0.3.34.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `393cfddaa410eed7551e1bc1ac036243ddfebb832973da01503f1a86cce82da2` |
| `docs/RELEASE_0.3.35.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `29db67bb08e3d7f567599903d9120fdb93c8e77ea7454c7857bfe23364b46110` |
| `docs/RELEASE_0.3.36.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `55f9dbf45b79fee64ef2f8da91f3726d601806a7b5043fe7ac9d1d50110a0bc1` |
| `docs/RELEASE_0.3.37.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `fca3e6384320c22130278e29e3142c26f5eae60ebdf8eb4b389e81c937d4c361` |
| `docs/RELEASE_0.3.38.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `43e74eb4fdfd2fbf5fcfae91c26b4cadaef6c5ea9c40d5f586cf67fc7339d43b` |
| `docs/RELEASE_0.3.39.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `987773d091e027ed4725fd0d6b79f993d17dbdf3c7cd7bde8bd540e10d79d2e5` |
| `docs/RELEASE_0.3.4.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `5dfd2b69021315259a5af5eb335da7d5d473c9e753705c8b0bfccbec08bfc4f0` |
| `docs/RELEASE_0.3.40.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `5a9876b2ba9461c5bb079ce8cba1bbc56486503f24d07172ca88232a60302326` |
| `docs/RELEASE_0.3.41.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `2ce280bbd4371dfd7de32428beac99db6012edfa734e2f2a10a7511845226da4` |
| `docs/RELEASE_0.3.5.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `fc4c505e7d1e0ca47233c904cec5999220346ae1d92b250110f717fbe61e74f0` |
| `docs/RELEASE_0.3.6.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `764a1ae94c41dbdbf729f93c24337d7635fef36a27bf00788dae67accd2a2ca5` |
| `docs/RELEASE_0.3.7.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `1cfb13b0c3ff1256c9439daa6be9e72885dbd5a723e6bc7ddfb6be40fb7134e9` |
| `docs/RELEASE_0.3.8.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `4ddc98b84b4c99e5f95cd6f7e48227d54277756313b275365dba962b87776516` |
| `docs/RELEASE_0.3.9.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `92c26d53ee8a2e15d385c1c5b14a6ad7e2b1bf40f41ff0d0d7abb120368f4fc9` |
| `docs/RELEASE_0.4.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `880c95fbdab5d1a56902b8fc3e4e145bfdf52b9906050f817b4b5fcd71578537` |
| `docs/RELEASE_0.4.1.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `35a35571f1db2b0b36bb964dd9eaa5dd232ef61d792766159c8e31791b3147d1` |
| `docs/RELEASE_0.4.2.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `ed318d80666377560e25a3347ab9972cf0ab80ddfd9fbfa5cfca5e5af4f2da74` |
| `docs/RELEASE_0.5.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `e04f4d0d3c6ebb3089733aa58d49f9638f3944066ceb6afed6d95ecce0da2352` |
| `docs/RELEASE_0.5.1.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `7d4eab983807f863e0f0e20b7a3658a7ef303c1587f8a9fe5092cfd878b4126f` |
| `docs/RELEASE_0.6.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `1d9bbfcecbc4734fdc6b6b2087b118d27b94fd944d2b89a1453d5275a765f213` |
| `docs/RELEASE_0.6.1.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `d30609367430836f7375ff5b60990300679c7f8441a944deda431318e9af12b5` |
| `docs/RELEASE_0.6.10.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `e951207d98c27d980a96ec3c2f6a85ff367ccf024480d9e605a1e24f68c2a617` |
| `docs/RELEASE_0.6.2.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `764df61eb230c1da4f606015d28767e7d95ff8e0eaba1ef7f4165ca33392910f` |
| `docs/RELEASE_0.6.3.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `837b886451394362a57ad9014c0972ff706dc272937fc399ace5e679ee05433d` |
| `docs/RELEASE_0.6.4.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `4cfa92735084cbcd24cfb93cbe37ac9c7fb14018d6531e972f24a7272cabd17f` |
| `docs/RELEASE_0.6.5.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `20abd2fa0a8b531910a153fb9a3cc96a19fa1b7bfbb45466f8455c08cdcae6f5` |
| `docs/RELEASE_0.6.6.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `34e5a88a5b81cb812e533752620d3c020226e965e06d4dd039b7ee9f19b007e5` |
| `docs/RELEASE_0.6.7.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `6624c11bd3afea7fcd1ada76dd36dc30755ad3cfc17d5bab51a7216fb97c70d5` |
| `docs/RELEASE_0.6.8.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `6c57186c11af5411d9013d3077f7d7108ddd727ccca00b984bf578521f8dc5c2` |
| `docs/RELEASE_0.6.9.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `0aa2ce48cf8298350798be2cbbeda85f297b8a6bcc76df15dc751cb6b76659fc` |
| `docs/RELEASE_0.7.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `0f742cf540df4c3871bc27be6b8c2ef7886aaec68512171e1b0c313ad5cc5416` |
| `docs/RELEASE_0.8.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `96fc4127356985e9ef558e0b7b04ee0d00cbd6630f18a030a4499503eb5455c9` |
| `docs/RELEASE_0.8.1.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `54bc3d7f5cf58e80a8792c31f88a7344805b5535b316c244a83e8f1f2b3f299f` |
| `docs/RELEASE_0.9.0.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `d7c86229d5823728c81720459ad27d85cd3e5196e340adbb8f0374f641ae95a1` |
| `docs/RELEASE_0.9.1.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `62da4ad70fa2848df73cc88700e05bc1d882437eba2b5ab8ce968bb626612210` |
| `docs/RELEASE_0.9.2.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `acf65bc3882af2555668c1a716584954596ba0930faf2a641d6f50b37a517b96` |
| `docs/RELEASE_0.9.3.md` | C | Historical evidence examples only; reusable evidence fields, no historical facts copied. | `eaba9193acb1e68bbee926303bdde6468552dcbcc4122b5d61e3a3bdd5ee895a` |
| `docs/ROADMAP_0.4.0.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `e2c8dc96cc6d75413c2f93263ccbe26d576bd00d66aea7bff53d26a8b602356a` |
| `docs/S108_REMOTE_PROVIDER_IMPLEMENTATION.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `606567a662d90ae1787eab36f1fdca9d9c0023376a938c749abe166d3fa5846a` |
| `docs/SECURITY.md` | B | Secret preservation, key recovery and audit-truth principles; remove local security roles, models, commands and protocols. | `ac80b54b54aa3d773a65c69dd35d0ce38c0f5d222f9edfc238c76cf7359096ae` |
| `docs/STORAGE_MIGRATION_RUNBOOK.md` | B | Extract process invariants; remove local tools, identifiers, roles, storage topology, brands and product gates. | `629ab9f5b0a47974f6b0dfddb5f8db215cc1edc62ebd25304b4293169b4339d3` |
| `docs/UI_LIST_STANDARD.md` | B | Extract process invariants; remove local tools, identifiers, roles, storage topology, brands and product gates. | `befc2fdb77a11d3265970144b2ad566e14f2b97f99b48d06e2ad630dde495ffc` |
| `docs/USER_GUIDE.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `b9f28fefed53792a22003777cf5613fdca720b41f6ac8c9dfb60be6456a80822` |
| `docs/governance/CAPABILITY_CATALOG_POLICY.md` | B | Extract process invariants; remove local tools, identifiers, roles, storage topology, brands and product gates. | `0bf5a15d02d51ebf10c2e47c8c257bbbd8fbe6a92b22d5f3b183e10b111d2d2d` |
| `docs/governance/DOCUMENT_GOVERNANCE.md` | B | Extract process invariants; remove local tools, identifiers, roles, storage topology, brands and product gates. | `3d59ad4e9e18caeb2723c0abddffe3d60d94e207d6ca0ebf2d2d16f010cf7ecc` |
| `docs/governance/NAVIGATION_INFORMATION_ARCHITECTURE.md` | B | Only generic route/access/presentation principle extracted; product/domain navigation and all concrete structures excluded. | `34ee0a1cc5c7ad3fdd2cbdab27c298fb5aaad53d1aabdac4684bccb0666a0a7f` |
| `docs/governance/ROADMAP_CHANGELOG.md` | C | Retain document ownership/structure only; replace all project facts with placeholders. | `d35acd9c4f59db19e315b9c7bd38e7e343dd3206293f806cd6cebb3dcd6eaf09` |
| `docs/governance/UI_IMPLEMENTATION_STANDARD.md` | B | Extract process invariants; remove local tools, identifiers, roles, storage topology, brands and product gates. | `bd82639cbe3463c24f2d978fb1102e3a56257cc9f766e7ca3ff958d44795e111` |
| `docs/pre-production/README.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `431ffba4d01630ddb1829722121daaebf9fe31a11d70f323cd8e8b5089a02ac5` |
| `docs/pre-production/data_processing_agreement.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `8a5a5e664e8920e8bdd291c1836f93a30d5916ba512f42289bb823f070873c04` |
| `docs/pre-production/membership_terms.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `da42450ebc4a25b787fe089ed696fbf615237d20ab88f9c5188de565eae06e71` |
| `docs/pre-production/privacy_notice.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `6651ccaea13fee4d70e982497f6f7e84418c595c1608de1aeaedd9bac48679a3` |
| `docs/pre-production/security_addendum.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `96b9dbfdb1e56c5e9134734d739cc389a0a29ffb366924046393abdb739ef841` |
| `docs/pre-production/service_agreement.md` | D | Product/domain, legal text or local operations content; do not import into standard. | `4c884869088518b36e1e76087bf8d4a00c060adb696b70f32fd3ca7ea984ae50` |
| `PROJECT_STATE.json` | C | State schema/metadata separation; no releases copied. | `15241ecb716713bfac1b53f42563abc32979fdd38d616c70b7020d968135c2dc` |
| `pyproject.toml` | B | Dependency/version metadata consistency; no runtime dependencies copied. | `c676d63d6afa0348c7c324330c8498985697407e0fe0b558c094b6a6aca2ff98` |
| `scripts/release_source_fingerprint.py` | B | Exact source plus runner/dependency identity; algorithm principles only. | `f477fcb4773104988c82bb66d0e55bbf888ec6b37e91cca05b03de7c18b107f9` |
| `scripts/projected_closure_gate.py` | B | Pre/post closure semantic consistency; no hardcoded transitions copied. | `efacd15f15a38c36bff64dcffdce72739edc2d1b94f6d487bd54910ccad40f0e` |
| `scripts/release_attestation.py` | B | Candidate-external evidence identity; no release tool copied. | `dc74be72917bf3b5ff3ae3b48fb776a74b0dfc551115e85ef045fc196b8b74fe` |
| `scripts/release_baseline.py` | B | Immutable baseline from explicit source reference; no packaging tool copied. | `99db2b53bd4e5f82c7c6b390f15f5997a0757ed0794a2bc8c706e5fa5251b527` |
| `scripts/release_candidate.py` | B | Immutable source snapshot and reproducible identity; principles only. | `5c1c49a112c508db66e55dbc55ba5ccd3b8de3824f0ff1c80e48f2bd0996ba2d` |
| `scripts/release_workflow.py` | B | Fail-closed promotion and separate technical/production gates; no commands copied. | `f7bd22f8af075e12bb29e4ca1d3c0d02b77296ac66206791e8e3a2ad3d11ba05` |
| `scripts/release_metadata_preflight.py` | B | Metadata and gate alignment; remove app-specific preflight implementation. | `c6d5a480e54d22d63718e13308c0169e990648c82f921824cd35de91412b841e` |
| `scripts/build_handoff_package.py` | B | Sanitized full-source transfer; no builder copied. | `6f67a9bef9f5f5470100cf3e6bcb7c589953dbfdacc010650e2384644c4e5970` |
| `scripts/build_package.py` | B | Artifact/runtime exclusion and preserved persistent state; no builder copied. | `1cfc79de5d0757d7b5ac34e5def89c2226ce77495132936e7d061cd2302d519d` |
| `screenshot-qa/manifest.json` | C | Surface/viewport/theme coverage structure only. | `1ca1e30b0ad73a2620e18afb0f11d177a608b3d3ad833c7ca5cbf5c2e350c3dc` |
| `scripts/screenshot_qa.mjs` | B | Disposable synthetic browser evidence; no runner copied. | `efd9c4f8bec2b3906076897466f7e40fe8efb0494d72f0e46badaab92cd757ab` |
| `scripts/screenshot_compare.mjs` | B | Explicit comparison/noise policy; no comparator copied. | `e88faea642d34934855c0ff45370c38a47b0108b1cd4838ce40fb2bc96718c3d` |
| `.gitignore` | B | Runtime/generated exclusions adapted to each consumer. | `96851d0577aa250d2330ca60632d92883d77a9758f25beb41335c1994c3b6724` |

## Reconciliation qualification — 2026-09-26

This historical candidate/hash inventory is not a rule-level semantic-equivalence claim. The navigation source row is corrected to B for its narrow generic principle; business/navigation structures remain excluded. The full semantic audit and explicit user decisions are recorded in [NEW_POLICY_REGISTER.md](NEW_POLICY_REGISTER.md) and [PROVENANCE.md](PROVENANCE.md). Prior Stage 1 bytes were DRAFT/RC; final status is owned by [RECONCILIATION_VALIDATION.md](RECONCILIATION_VALIDATION.md).
