import 'dart:convert';
import 'dart:io';
import 'package:bfrbsys/api/http_service.dart';
import 'package:bfrbsys/api/models/models.dart';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:csv/csv.dart';

class NeuralNetworkRequestBuild {
  HttpService httpService = HttpService();
  late Future<TrainedModels> _futureModel;

  Future<Map<String, dynamic>> get response {
    return _futureModel.then((value) {
      return value.toJson();
    });
  }

  Future<TrainedModels> get model {
    return _futureModel;
  }

  void build({
    required String fileEncoded,
    required String modelName,
    required String userToken,
  }) {
    _futureModel = httpService.postModel(
      fileEncoded: fileEncoded,
      modelName: modelName,
      userToken: userToken,
    );
  }

  void sendInput({
    required String filePath,
    required String modelName,
    required String userToken,
  }) {
    _futureModel = httpService.sendInput(
      filePath: filePath,
      modelName: modelName,
      userToken: userToken,
    );
  }
}
